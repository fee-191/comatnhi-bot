import discord
import asyncio
import random
import yt_dlp
from discord.ext import commands
from utils import format_time, create_now_playing_embed, create_queue_embed
 
# ==================== YT-DLP CONFIG ====================
YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'playlist_items': '1',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

YTDL_PLAYLIST_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0',
    'extract_flat': True,
}
 
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}
 
# ==================== TRACK CLASS ====================
class Track:
    def __init__(self, data, requester=None):
        self.title = data.get('title', 'Unknown')
        self.uri = data.get('webpage_url', data.get('url', ''))
        self.stream_url = data.get('url', '')
        self.length = (data.get('duration') or 0) * 1000
        self.artwork = data.get('thumbnail', '')
        self.source = 'youtube'
        self.author = data.get('uploader', '')
        self.requester = requester
 
    @classmethod
    async def search(cls, query, requester=None):
        loop = asyncio.get_event_loop()
        is_url = query.startswith('http')
        is_playlist = is_url and ('list=' in query or '/playlist' in query)
        
        if is_playlist:
            # Load playlist
            def extract_playlist():
                with yt_dlp.YoutubeDL(YTDL_PLAYLIST_OPTIONS) as ydl:
                    return ydl.extract_info(query, download=False)
            data = await loop.run_in_executor(None, extract_playlist)
            if 'entries' in data:
                tracks = []
                for e in data['entries']:
                    if not e:
                        continue
                    # Tạo track với thông tin cơ bản, stream URL sẽ fetch sau
                    t = cls.__new__(cls)
                    t.title = e.get('title', 'Unknown')
                    t.uri = f"https://www.youtube.com/watch?v={e.get('id', '')}" if e.get('id') else e.get('url', '')
                    t.stream_url = ''
                    t.length = (e.get('duration') or 0) * 1000
                    t.artwork = e.get('thumbnail', '')
                    t.source = 'youtube'
                    t.author = e.get('uploader', '')
                    t.requester = requester
                    tracks.append(t)
                return tracks
            return [cls(data, requester)]
        else:
            search_query = query if is_url else f'ytsearch5:{query}'
            def extract():
                with yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS) as ydl:
                    return ydl.extract_info(search_query, download=False)
            data = await loop.run_in_executor(None, extract)
            if 'entries' in data:
                return [cls(e, requester) for e in data['entries'] if e]
            return [cls(data, requester)]
 
    async def get_stream_url(self):
        """Re-extract stream URL ngay lúc play để tránh expire"""
        loop = asyncio.get_event_loop()
        def extract():
            with yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS) as ydl:
                return ydl.extract_info(self.uri, download=False)
        data = await loop.run_in_executor(None, extract)
        return data.get('url', self.stream_url)
 
# ==================== PLAYER CLASS ====================
class MusicPlayer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.vc = None
        self.queue = []
        self.current = None
        self.volume = 100
        self.loop = False
        self.loop_queue = False
        self.last_msg = None
        self._idle_task = None
 
    @property
    def playing(self):
        return self.vc and self.vc.is_playing()
 
    @property
    def paused(self):
        return self.vc and self.vc.is_paused()
 
    @property
    def connected(self):
        return self.vc and self.vc.is_connected()
 
    def schedule_idle_disconnect(self):
        if self._idle_task:
            self._idle_task.cancel()
        self._idle_task = asyncio.create_task(self._idle_disconnect())
 
    async def _idle_disconnect(self):
        await asyncio.sleep(300)
        if self.connected and not self.playing and not self.paused:
            await self.vc.disconnect()
 
    async def play_next(self):
        if self.loop and self.current:
            track = self.current
        elif self.queue:
            track = self.queue.pop(0)
            if self.loop_queue and self.current:
                self.queue.append(self.current)
        else:
            self.current = None
            if self.last_msg:
                try:
                    await self.last_msg.delete()
                except:
                    pass
            self.schedule_idle_disconnect()
            return
 
        self.current = track
        try:
            stream_url = await track.get_stream_url()
            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=self.volume / 100)
            self.vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._after_play(e), self.ctx.bot.loop
            ))
            await self._send_interface()
        except Exception as e:
            print(f"❌ Lỗi phát nhạc: {e}")
            await self.ctx.channel.send(f"❌ Lỗi phát: `{e}`", delete_after=10)
            await self.play_next()
 
    async def _after_play(self, error):
        if error:
            print(f"❌ Player error: {error}")
        await self.play_next()
 
    async def _send_interface(self):
        if self.last_msg:
            try:
                await self.last_msg.delete()
            except:
                pass
        view = MusicController(self)
        embed = create_now_playing_embed(self, self.current)
        self.last_msg = await self.channel.send(embed=embed, view=view)
 
    def set_volume(self, vol):
        self.volume = vol
        if self.vc and self.vc.source:
            self.vc.source.volume = vol / 100
 
    def skip(self):
        self.loop = False
        if self.vc:
            self.vc.stop()
 
    def stop_all(self):
        self.loop = False
        self.loop_queue = False
        self.queue.clear()
        if self.vc:
            self.vc.stop()
 
# ==================== UI: TAB ====================
class TabSelect(discord.ui.Select):
    def __init__(self, player):
        self.player = player
        options = [
            discord.SelectOption(label="Đang phát", emoji="🎵", value="nowplaying", default=True),
            discord.SelectOption(label="Hàng chờ",  emoji="📋", value="queue"),
        ]
        super().__init__(placeholder="📂 Chọn tab...", options=options, row=0)
 
    async def callback(self, interaction: discord.Interaction):
        view: MusicController = self.view
        if self.values[0] == "nowplaying":
            for opt in self.options:
                opt.default = (opt.value == "nowplaying")
            view.set_tab("nowplaying")
            embed = create_now_playing_embed(self.player, self.player.current)
        else:
            for opt in self.options:
                opt.default = (opt.value == "queue")
            view.set_tab("queue")
            embed = create_queue_embed(self.player)
        await interaction.response.edit_message(embed=embed, view=view)
 
# ==================== UI: XÓA BÀI ====================
class RemoveSelect(discord.ui.Select):
    def __init__(self, player):
        self.player = player
        options = []
        for i, t in enumerate(player.queue[:20], 1):
            label = t.title[:95] + "..." if len(t.title) > 95 else t.title
            options.append(discord.SelectOption(
                label=f"{i}. {label}",
                value=str(i - 1),
                description=f"⏱️ {format_time(t.length)}"
            ))
        if not options:
            options = [discord.SelectOption(label="Hàng chờ trống", value="empty", emoji="❌")]
        super().__init__(
            placeholder="🗑️ Chọn bài muốn xóa...",
            options=options, row=1,
            disabled=(not options or options[0].value == "empty")
        )
 
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "empty":
            return await interaction.response.send_message("❌ Hàng chờ trống!", ephemeral=True)
        index = int(self.values[0])
        if index >= len(self.player.queue):
            return await interaction.response.send_message("❌ Bài không còn trong queue.", ephemeral=True)
        removed = self.player.queue.pop(index)
        view: MusicController = self.view
        view.refresh_queue_tab(self.player)
        embed = create_queue_embed(self.player)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(f"🗑️ Đã xóa **{removed.title}**", ephemeral=True)
 
# ==================== UI: TỐC ĐỘ ====================
class FilterSelect(discord.ui.Select):
    def __init__(self, player):
        self.player = player
        options = [
            discord.SelectOption(label="0.5x (Rất chậm)", emoji="🐢", value="0.5"),
            discord.SelectOption(label="0.75x (Chậm)",    emoji="🐌", value="0.75"),
            discord.SelectOption(label="1.0x (Chuẩn)",    emoji="💿", value="1.0"),
            discord.SelectOption(label="1.25x (Nhanh)",   emoji="🏃", value="1.25"),
            discord.SelectOption(label="1.5x (Rất nhanh)",emoji="🚀", value="1.5"),
            discord.SelectOption(label="2.0x (Siêu tốc)", emoji="⚡", value="2.0"),
        ]
        super().__init__(placeholder="⏱️ Tốc độ phát...", min_values=1, max_values=1, options=options, row=1)
 
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚠️ Tính năng tốc độ chưa hỗ trợ với engine hiện tại.", ephemeral=True)

# ==================== UI: BẢNG ĐIỀU KHIỂN ====================
class MusicController(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player
        self.current_tab = "nowplaying"
        self._build_nowplaying_tab()
 
    def _build_nowplaying_tab(self):
        self.clear_items()
        self.add_item(TabSelect(self.player))
        self.add_item(FilterSelect(self.player))
        for btn in self._nowplaying_buttons():
            self.add_item(btn)
 
    def _nowplaying_buttons(self):
        pause_btn   = discord.ui.Button(emoji="⏯️", style=discord.ButtonStyle.success,   row=2, custom_id="pause")
        skip_btn    = discord.ui.Button(emoji="⏭️", style=discord.ButtonStyle.primary,   row=2, custom_id="skip")
        stop_btn    = discord.ui.Button(emoji="⏹️", style=discord.ButtonStyle.danger,    row=2, custom_id="stop")
        loop_style  = discord.ButtonStyle.success if self.player.loop else discord.ButtonStyle.secondary
        lq_style    = discord.ButtonStyle.success if self.player.loop_queue else discord.ButtonStyle.secondary
        loop_btn    = discord.ui.Button(emoji="🔂", style=loop_style,                    row=3, custom_id="loop")
        loopq_btn   = discord.ui.Button(emoji="🔁", style=lq_style,                      row=3, custom_id="loopqueue")
        shuffle_btn = discord.ui.Button(emoji="🔀", style=discord.ButtonStyle.secondary, row=3, custom_id="shuffle")
        vold_btn    = discord.ui.Button(emoji="🔉", label="-", style=discord.ButtonStyle.secondary, row=4, custom_id="vol_down")
        volu_btn    = discord.ui.Button(emoji="🔊", label="+", style=discord.ButtonStyle.secondary, row=4, custom_id="vol_up")
        pause_btn.callback   = self._pause_callback
        skip_btn.callback    = self._skip_callback
        stop_btn.callback    = self._stop_callback
        loop_btn.callback    = self._loop_callback
        loopq_btn.callback   = self._loopqueue_callback
        shuffle_btn.callback = self._shuffle_callback
        vold_btn.callback    = self._vol_down_callback
        volu_btn.callback    = self._vol_up_callback
        return [pause_btn, skip_btn, stop_btn, loop_btn, loopq_btn, shuffle_btn, vold_btn, volu_btn]
 
    def _build_queue_tab(self):
        self.clear_items()
        self.add_item(TabSelect(self.player))
        for item in self.children:
            if isinstance(item, TabSelect):
                for opt in item.options:
                    opt.default = (opt.value == "queue")
        self.add_item(RemoveSelect(self.player))
        clearall_btn = discord.ui.Button(label="🧹 Xóa tất cả", style=discord.ButtonStyle.danger,    row=2, custom_id="clearall")
        shuffle_btn  = discord.ui.Button(emoji="🔀",             style=discord.ButtonStyle.secondary, row=2, custom_id="q_shuffle")
        clearall_btn.callback = self._clearall_callback
        shuffle_btn.callback  = self._q_shuffle_callback
        self.add_item(clearall_btn)
        self.add_item(shuffle_btn)
 
    def set_tab(self, tab):
        self.current_tab = tab
        if tab == "nowplaying":
            self._build_nowplaying_tab()
        else:
            self._build_queue_tab()
 
    def refresh_queue_tab(self, player):
        self.player = player
        self._build_queue_tab()
 
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.player.connected:
            await interaction.response.send_message("❌ Bot đã ngắt kết nối.", ephemeral=True)
            return False
        return True
 
    async def _pause_callback(self, interaction: discord.Interaction):
        if self.player.paused:
            self.player.vc.resume()
        else:
            self.player.vc.pause()
        self._build_nowplaying_tab()
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
 
    async def _skip_callback(self, interaction: discord.Interaction):
        self.player.skip()
        await interaction.response.send_message("⏭️ Đã qua bài.", ephemeral=True)
 
    async def _stop_callback(self, interaction: discord.Interaction):
        self.player.stop_all()
        self.player.schedule_idle_disconnect()
        self.stop()
        await interaction.response.send_message("⏹️ Đã dừng phát.", ephemeral=True)
 
    async def _loop_callback(self, interaction: discord.Interaction):
        self.player.loop = not self.player.loop
        if self.player.loop:
            self.player.loop_queue = False
            msg = "🔂 Đã bật lặp **1 bài**!"
        else:
            msg = "🔂 Đã tắt lặp bài."
        self._build_nowplaying_tab()
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(msg, ephemeral=True)
 
    async def _loopqueue_callback(self, interaction: discord.Interaction):
        self.player.loop_queue = not self.player.loop_queue
        if self.player.loop_queue:
            self.player.loop = False
            msg = "🔁 Đã bật lặp **cả queue**!"
        else:
            msg = "🔁 Đã tắt lặp queue."
        self._build_nowplaying_tab()
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(msg, ephemeral=True)
 
    async def _shuffle_callback(self, interaction: discord.Interaction):
        if not self.player.queue:
            return await interaction.response.send_message("❌ Hàng chờ trống!", ephemeral=True)
        random.shuffle(self.player.queue)
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("🔀 Đã trộn hàng chờ!", ephemeral=True)
 
    async def _vol_down_callback(self, interaction: discord.Interaction):
        self.player.set_volume(max(self.player.volume - 10, 0))
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
 
    async def _vol_up_callback(self, interaction: discord.Interaction):
        self.player.set_volume(min(self.player.volume + 10, 200))
        embed = create_now_playing_embed(self.player, self.player.current)
        await interaction.response.edit_message(embed=embed, view=self)
 
    async def _clearall_callback(self, interaction: discord.Interaction):
        if not self.player.queue:
            return await interaction.response.send_message("❌ Hàng chờ đã trống.", ephemeral=True)
        count = len(self.player.queue)
        self.player.queue.clear()
        self.refresh_queue_tab(self.player)
        embed = create_queue_embed(self.player)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🧹 Đã xóa **{count} bài**.", ephemeral=True)
 
    async def _q_shuffle_callback(self, interaction: discord.Interaction):
        if not self.player.queue:
            return await interaction.response.send_message("❌ Hàng chờ trống!", ephemeral=True)
        random.shuffle(self.player.queue)
        self.refresh_queue_tab(self.player)
        embed = create_queue_embed(self.player)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("🔀 Đã trộn hàng chờ!", ephemeral=True)
 
# ==================== COG: MUSIC ====================
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
 
    def get_player(self, ctx):
        gid = ctx.guild.id
        if gid not in self.players:
            self.players[gid] = MusicPlayer(ctx)
        return self.players[gid]
 
    async def cog_unload(self):
        for player in self.players.values():
            if player.connected:
                await player.vc.disconnect()
 
    @commands.command()
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Hãy vào phòng voice trước!")
        player = self.get_player(ctx)
        player.ctx = ctx
        player.channel = ctx.channel
        if ctx.voice_client:
            player.vc = ctx.voice_client
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
        elif not player.connected:
            vc = await ctx.author.voice.channel.connect()
            player.vc = vc
 
        async with ctx.typing():
            try:
                tracks = await Track.search(search, requester=ctx.author)
            except Exception as e:
                return await ctx.send(f"❌ Lỗi tìm kiếm: {e}")
            if not tracks:
                return await ctx.send("❌ Không tìm thấy bài nào.")
 
        track = tracks[0]
        if not player.playing and not player.paused:
            player.queue.insert(0, track)
            await player.play_next()
        else:
            player.queue.append(track)
            await ctx.send(f"✅ Đã thêm **{track.title}** vào hàng chờ.", delete_after=5)
            try:
                await ctx.message.delete()
            except:
                pass

    @commands.command()
    async def search(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Hãy vào phòng voice trước!")
        async with ctx.typing():
            try:
                tracks = await Track.search(query, requester=ctx.author)
            except Exception as e:
                return await ctx.send(f"❌ Lỗi: {e}")
        if not tracks:
            return await ctx.send("❌ Không tìm thấy bài nào.")
        results = tracks[:5]
        embed = discord.Embed(title=f"🔍 Kết quả: {query}", color=0x3498db)
        desc = ""
        for i, t in enumerate(results, 1):
            desc += f"`{i}.` **{t.title}**\n　🎵 `youtube` | ⏱️ `{format_time(t.length)}`\n\n"
        embed.description = desc
        embed.set_footer(text="Gõ số 1-5 để chọn | Gõ 'hủy' để thoát")
        msg = await ctx.send(embed=embed)
 
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
 
        try:
            reply = await self.bot.wait_for("message", check=check, timeout=30)
            await msg.delete()
            try:
                await reply.delete()
            except:
                pass
            if reply.content.lower() in ["hủy", "cancel", "h"]:
                return await ctx.send("❌ Đã hủy.", delete_after=5)
            index = int(reply.content) - 1
            if not 0 <= index < len(results):
                return await ctx.send("❌ Số không hợp lệ.", delete_after=5)
            track = results[index]
            player = self.get_player(ctx)
            player.ctx = ctx
            player.channel = ctx.channel
            if not player.connected:
                vc = await ctx.author.voice.channel.connect()
                player.vc = vc
            if not player.playing and not player.paused:
                player.queue.insert(0, track)
                await player.play_next()
            else:
                player.queue.append(track)
                await ctx.send(f"✅ Đã thêm **{track.title}** vào hàng chờ.", delete_after=5)
        except (ValueError, IndexError):
            await ctx.send("❌ Vui lòng nhập số từ 1-5.", delete_after=5)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("⏱️ Hết thời gian.", delete_after=5)
 
    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ Hãy vào phòng voice trước!")
        player = self.get_player(ctx)
        if not player.connected:
            vc = await ctx.author.voice.channel.connect()
            player.vc = vc
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("⚠️ Bot đang ở trong phòng rồi.")
 
    @commands.command()
    async def leave(self, ctx):
        player = self.get_player(ctx)
        # Reset AFK nếu đang dùng
        if getattr(self.bot, '_afk_owner', None) == ctx.author.id or \
           getattr(self.bot, '_afk_owner', None) is not None:
            self.bot._afk_owner = None
        if player.connected:
            player.stop_all()
            await player.vc.disconnect()
            self.players.pop(ctx.guild.id, None)
            await ctx.message.add_reaction("👋")
 
    @commands.command()
    async def stop(self, ctx):
        player = self.get_player(ctx)
        if player.connected:
            player.stop_all()
            player.schedule_idle_disconnect()
            await ctx.send("⏹️ Đã dừng phát.")
 
    @commands.command()
    async def skip(self, ctx):
        player = self.get_player(ctx)
        if player.playing or player.paused:
            player.skip()
            await ctx.message.add_reaction("⏭️")
 
    @commands.command()
    async def pause(self, ctx):
        player = self.get_player(ctx)
        if player.playing:
            player.vc.pause()
            await ctx.message.add_reaction("⏸️")
        elif player.paused:
            player.vc.resume()
            await ctx.message.add_reaction("▶️")
 
    @commands.command()
    async def now(self, ctx):
        player = self.get_player(ctx)
        if player.current:
            try:
                await ctx.message.delete()
            except:
                pass
            if player.last_msg:
                try:
                    await player.last_msg.delete()
                except:
                    pass
            view = MusicController(player)
            embed = create_now_playing_embed(player, player.current)
            player.last_msg = await ctx.channel.send(embed=embed, view=view)
        else:
            await ctx.send("❌ Chưa có nhạc đang phát.", delete_after=5)
 
    @commands.command()
    async def vol(self, ctx, volume: int):
        if not 0 <= volume <= 200:
            return await ctx.send("❌ Âm lượng phải từ 0 đến 200.", delete_after=5)
        player = self.get_player(ctx)
        player.set_volume(volume)
        await ctx.send(f"🔊 Âm lượng: {volume}%", delete_after=5)
 
    @commands.command()
    async def queue(self, ctx):
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("❌ Chưa có nhạc.", delete_after=5)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(embed=create_queue_embed(player), delete_after=30)
 
    @commands.command()
    async def remove(self, ctx, index: int):
        player = self.get_player(ctx)
        if not player.queue:
            return await ctx.send("❌ Hàng chờ trống.", delete_after=5)
        if not 1 <= index <= len(player.queue):
            return await ctx.send(f"❌ Số từ 1 đến {len(player.queue)}.", delete_after=5)
        removed = player.queue.pop(index - 1)
        await ctx.send(f"🗑️ Đã xóa **{removed.title}**.", delete_after=5)
        try:
            await ctx.message.delete()
        except:
            pass
 
    @commands.command()
    async def clearqueue(self, ctx):
        player = self.get_player(ctx)
        if not player.queue:
            return await ctx.send("❌ Hàng chờ đã trống.", delete_after=5)
        count = len(player.queue)
        player.queue.clear()
        await ctx.send(f"🗑️ Đã xóa **{count} bài**.", delete_after=5)
 
    @commands.command()
    async def move(self, ctx, from_pos: int, to_pos: int):
        player = self.get_player(ctx)
        total = len(player.queue)
        if not player.queue:
            return await ctx.send("❌ Hàng chờ trống.", delete_after=5)
        if not (1 <= from_pos <= total) or not (1 <= to_pos <= total):
            return await ctx.send(f"❌ Vị trí từ 1 đến {total}.", delete_after=5)
        track = player.queue.pop(from_pos - 1)
        player.queue.insert(to_pos - 1, track)
        await ctx.send(f"↕️ Đã chuyển **{track.title}** từ `{from_pos}` → `{to_pos}`", delete_after=8)
 
    @commands.command()
    async def shuffle(self, ctx):
        player = self.get_player(ctx)
        if not player.queue:
            return await ctx.send("❌ Hàng chờ trống.", delete_after=5)
        random.shuffle(player.queue)
        await ctx.send("🔀 Đã trộn hàng chờ!", delete_after=5)
 
    @commands.command()
    async def loop(self, ctx):
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("❌ Chưa có nhạc.", delete_after=5)
        player.loop = not player.loop
        if player.loop:
            player.loop_queue = False
        state = "🔂 Đã bật" if player.loop else "⏹️ Đã tắt"
        await ctx.send(f"{state} lặp bài **{player.current.title}**", delete_after=10)
 
    @commands.command()
    async def loopqueue(self, ctx):
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("❌ Chưa có nhạc.", delete_after=5)
        player.loop_queue = not player.loop_queue
        if player.loop_queue:
            player.loop = False
        state = "🔁 Đã bật" if player.loop_queue else "⏹️ Đã tắt"
        await ctx.send(f"{state} lặp queue", delete_after=10)
 
# ==================== SETUP ====================
async def setup(bot):
    await bot.add_cog(Music(bot))
