import re
from discord.ext import commands
from discord_components import Button
import lavalink
import discord

url_rx = re.compile(r'https?://(?:www\.)?.+')

class MusicCog(commands.Cog):
    """ Cog for commands related to the genral use of the lavalink player. """
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('localhost', 7000, 'testing', 'na', 'music-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')
        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """
        Unload Handler. Removes event hooks.
        """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Checks if bot is in guild and ensures voice before invoing commands. """
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        """ Checks if author and player are in the same voice channel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        #Commands that dont require the bot to be in a voice channel need to be listed here.
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
        """ Disconnects from channel when queue ends. """
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Helper ro connect to passsed voice channel"""
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """ Handles the querying and adding of tracks to the queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        query = query.strip('<>')
        last_message = ctx.channel.last_message
        edit_instead = False

        # Querying for tracks
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            embed.description = 'Nothing found!'
            return await ctx.send(embed = embed)

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            #embed building
            embed.title = 'Playlist Enqueued:'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            if not url_rx.match(query):
                edit_instead = True
                tracks = results['tracks'][:5]

                embed.description = ''
                i = 0
                for track in tracks:
                    i = i + 1
                    embed.description = embed.description + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]}) - {track["info"]["author"]}\n'
                await ctx.reply(
                    embed = embed,
                    components = [
                        [
                            Button(label = "1", custom_id = "1"),
                            Button(label = "2", custom_id = "2"),
                            Button(label = "3", custom_id = "3"),
                            Button(label = "4", custom_id = "4"),
                            Button(label = "5", custom_id = "5"),
                        ]
                    ]
                )
                last_message = ctx.channel.last_message
                interaction = await self.bot.wait_for('button_click', check= lambda i: i.author==ctx.author)
                track = tracks[int(interaction.custom_id)-1]
                await interaction.edit_origin(components = [])
                await interaction.send(content="Enqueued")
            else:
                track = results['tracks'][0]

            #embed building
            embed.title = 'Track Enqueud'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]}) - {track["info"]["author"]}'

            #enqueueing track
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        #edit last message instead of sending if preferred
        if edit_instead:
            await last_message.edit(embed = embed)
        else:
            await ctx.reply(embed = embed)

        #connects player and starts if not already in channel and playing
        if not player.is_playing:
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            await player.play()

    @commands.command(aliases=['leave', 'dc',])
    async def disconnect(self, ctx):
        """ Disconnects from the connected voice channel. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.reply('Not Connected')
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.reply('You\'re not in my voice channel')
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        return await ctx.reply('Disco-nnected')

    @commands.command(aliases=['next'])
    async def skip(self, ctx, *args):
        """ Skips to the next track in the queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if len(args)<1:
            await player.skip()
            return await ctx.reply('Skipped 1 song')
        else:
            if args[0].isdigit():
                i = int(args[0])
                j = i
                while(i>0 and player.is_playing):
                    i = i - 1
                    await player.skip()
                return await ctx.reply(f'Skipped {j-i} songs')

    @commands.command(aliases=['unpause', 'stop', 'start'])
    async def pause(self, ctx, *args):
        """ Pauses the player. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        await player.set_pause(not player.paused)
        if player.paused:
            embed.title = 'Paused'
        else:
            embed.title = 'Unpaused'
        embed.description = f'[{player.current.title}]({player.current.uri}) - {player.current.author}'
        return await ctx.reply(embed = embed)

    @commands.command(aliases=['vol',])
    async def volume(self, ctx, *args):
        """ Shows and adjusts player volume. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if len(args)<1:
            return await ctx.reply(f'Volume is at {player.volume}%')
        else:
            if args[0].isdigit():
                new_volume = int(args[0])
                if new_volume > 200:
                    new_volume = 200
                await player.set_volume(new_volume)
                return await ctx.reply(f'Volume is now at {player.volume}%')

    @commands.command(aliases=['cur', 'curr',])
    async def current(self, ctx, *args):
        """ Displays information about the current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = f'Current Track'
        embed.description = f'[{player.current.title}]({player.current.uri}) - {player.current.author}'
        return await ctx.reply(embed = embed)

    @commands.command(aliases=['repeat',])
    async def loop(self, ctx, *args):
        """ Toggles queue looping. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.repeat = not player.repeat
        if player.repeat:
            return await ctx.reply('Looping queue.')
        else:
            return await ctx.reply('Stopped looping queue.')

    @commands.command(aliases=[])
    async def shuffle(self, ctx, *args):
        """ Toggles shuffling of the queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.set_shuffle(not player.shuffle)
        if player.shuffle:
             return await ctx.reply('Shuffling')
        else:
            return await ctx.reply('Stopped Shuffling')

def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(MusicCog(bot))
