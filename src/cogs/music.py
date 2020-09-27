import re

from discord.ext import commands
import lavalink
import discord

url_rx = re.compile(r'https?://(?:www\.)?.+')

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('localhost', 7000, 'testing', 'na', 'music-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')
        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        # Commands that dont require the bot to be in a voice channel need to be listed here
        should_connect = ctx.command.name in ('play', 'pick',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a Voice Channel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not Connected.')
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)
            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('I need the \'CONNECT\' AND \'SPEAK\' permissions.')
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('Already in a different voice channel.')

    async def track_hook(self, event):
        # When track_hook recieves a QueueEndEvent, disconnects from channel.
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        query = query.strip('<>')

        # Querying for tracks
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            embed.description = 'Nothing found!'
            return await ctx.send(embed = embed)

        if results['loadType'] == 'PLAYLIST LOADED':
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            embed.title = 'Playlist Enqueued:'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            if not url_rx.match(query):
                tracks = results['tracks'][:5]
                embed.title = 'Result:'
                embed.description = 'Use %%pick [int] in the next 30s:\n\n'
                i = 0
                for track in tracks:
                    i = i + 1
                    embed.description = embed.description + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]}) - {track["info"]["author"]}\n'
                await ctx.send(embed = embed)

                def check(m):
                    mList = m.content.strip('<>').split()
                    return m.author.id == ctx.author.id and ('%%' in mList[0])

                try:
                    response = await self.bot.wait_for('message', timeout = 30, check=check)
                    track = tracks[int(response.content.split(' ')[1])-1]
                except TimeoutError:
                    print(f'{ctx.author} didn\'t choose in time.')
                    return
                except Exception as e:
                    print(e)
                    return
            else:
                track = results['tracks'][0]
            embed.title = 'Track Enqueud'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]}) - {track["info"]["author"]}'
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed = embed)
        if not player.is_playing:
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            await player.play()

    @commands.command()
    async def pick(self, ctx):
        return

    @commands.command(aliases=['leave', 'dc',])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if not player.is_connected:
            embed.title = 'Not Connected'
            return await ctx.send(embed = embed)
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            embed.title = 'You\'re not in my voice channel'
            return await ctx.send(embed = embed)
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        embed.title = 'Disco-nnected'
        return await ctx.send(embed = embed)

    @commands.command(aliases=['next'])
    async def skip(self, ctx, *args):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if len(args)<1:
            await player.skip()
            embed.title = 'Skipped 1 song'
            return await ctx.send(embed = embed)
        else:
            if args[0].isdigit():
                i = int(args[0])
                j = i
                while(i>0 and player.is_playing):
                    i = i - 1
                    await player.skip()
                embed.title = f'Skipped {j-i} songs'
                return await ctx.send(embed = embed)

    @commands.command(aliases=['unpause',])
    async def pause(self, ctx, *args):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        await player.set_pause(not player.paused)
        if player.paused:
            embed.title = 'Paused'
        else:
            embed.title = 'Unpaused'
        embed.description = f'[{player.current.title}]({player.current.uri}) - {player.current.author}'
        return await ctx.send(embed = embed)

    @commands.command(aliases=['repeat',])
    async def loop(self, ctx, *args):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        player.repeat = not player.repeat
        if player.repeat:
            embed.title = f'Looping queue.'
        else:
            embed.title = f'Stopped looping queue.'
        return await ctx.send(embed = embed)

    @commands.command(aliases=['vol',])
    async def volume(self, ctx, *args):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        if len(args)<1:
            embed.title = f'Volume is at {player.volume}%'
            return await ctx.send(embed = embed)
        else:
            if args[0].isdigit():
                new_volume = int(args[0])
                if new_volume > 200:
                    new_volume = 200
                await player.set_volume(new_volume)
                embed.title = f'Volume is now at {player.volume}%'
                return await ctx.send(embed = embed)

    @commands.command(aliases=['cur', 'curr',])
    async def current(self, ctx, *args):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = f'Current Track'
        embed.description = f'[{player.current.title}]({player.current.uri}) - {player.current.author}'
        return await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(MusicCog(bot))
