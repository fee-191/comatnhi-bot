import discord
import urllib.parse
from discord.ext import commands
 
# ==================== UI: PHÂN TRANG HELP ====================
class HelpView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=60)
        self.pages = pages
        self.current = 0
        self._update_buttons()
 
    def _update_buttons(self):
        self.prev_btn.disabled = self.current == 0
        self.next_btn.disabled = self.current == len(self.pages) - 1
        self.page_btn.label = f"{self.current + 1} / {len(self.pages)}"
 
    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
 
    @discord.ui.button(label="1 / 5", style=discord.ButtonStyle.primary, disabled=True)
    async def page_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
 
    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
 
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass
 
 
def build_help_pages(bot) -> list[discord.Embed]:
 
    # ---------- Trang 1: Giới thiệu Bot ----------
    p1 = discord.Embed(
        title=f"🤖 {bot.user.name}",
        description="Cục cưng ngoan xinh yêu của các anh đây!\nDùng nút **◀ ▶** để xem các lệnh.",
        color=0xf1c40f
    )
    if bot.user.avatar:
        p1.set_thumbnail(url=bot.user.avatar.url)
    ping      = round(bot.latency * 1000)
    ping_icon = "🟢" if ping < 80 else ("🟡" if ping < 150 else "🔴")
    p1.add_field(name="🆔 ID",             value=f"`{bot.user.id}`",                        inline=True)
    p1.add_field(name="📅 Ngày tạo",       value=bot.user.created_at.strftime("%d/%m/%Y"),  inline=True)
    p1.add_field(name=f"{ping_icon} Ping", value=f"**{ping}ms**",                           inline=True)
    p1.add_field(name="🏠 Server",         value=f"**{len(bot.guilds)}** server",            inline=True)
    p1.add_field(name="👥 Thành viên",     value=f"**{sum(g.member_count for g in bot.guilds)}** người", inline=True)
    p1.add_field(name="🎵 Prefix",         value="`>`",                                     inline=True)
    p1.set_footer(text="Trang 1/5 — Giới thiệu Bot")
 
    # ---------- Trang 2: Phát nhạc ----------
    p2 = discord.Embed(title="🎵 Phát nhạc", color=0xe74c3c)
    p2.add_field(name="▶️ Cơ bản", value=(
        "`>play [tên/link]` — Phát nhạc hoặc thêm vào queue\n"
        "`>search [tên]` — Tìm kiếm và chọn từ top 5 kết quả\n"
        "`>now` — Hiện bảng điều khiển bài đang phát\n"
        "`>pause` — Tạm dừng / Tiếp tục\n"
        "`>skip` — Qua bài tiếp theo\n"
        "`>stop` — Dừng phát và xóa hàng chờ"
    ), inline=False)
    p2.add_field(name="🔊 Âm lượng & Kết nối", value=(
        "`>vol [0-200]` — Chỉnh âm lượng\n"
        "`>join` — Bot vào phòng voice của bạn\n"
        "`>leave` — Bot thoát phòng voice"
    ), inline=False)
    p2.set_footer(text="Trang 2/5 — Phát nhạc")
 
    # ---------- Trang 3: Hàng chờ & Loop ----------
    p3 = discord.Embed(title="📋 Hàng chờ & 🔄 Loop", color=0x9b59b6)
    p3.add_field(name="📝 Quản lý Queue", value=(
        "`>queue` — Xem danh sách hàng chờ\n"
        "`>remove [số]` — Xóa 1 bài theo số thứ tự\n"
        "`>clearqueue` — Xóa **toàn bộ** hàng chờ (giữ bài đang phát)\n"
        "`>move [từ] [đến]` — Đổi vị trí bài trong queue\n"
        "`>shuffle` — Trộn ngẫu nhiên hàng chờ"
    ), inline=False)
    p3.add_field(name="🔄 Loop", value=(
        "`>loop` — Bật/tắt lặp **1 bài** đang phát\n"
        "`>loopqueue` — Bật/tắt lặp **cả queue**\n"
        "*(Nút **🔂 🔁** trên panel cũng dùng được)*"
    ), inline=False)
    p3.add_field(name="💡 Ví dụ", value=(
        "`>move 5 1` → kéo bài thứ 5 lên đầu queue\n"
        "`>remove 3` → xóa bài thứ 3 khỏi queue"
    ), inline=False)
    p3.set_footer(text="Trang 3/5 — Hàng chờ & Loop")
 
    # ---------- Trang 4: Tiện ích ----------
    p4 = discord.Embed(title="🗣️ Tiện ích", color=0x3498db)
    p4.add_field(name="👤 Thành viên", value=(
        "`>avatar [@user]` — Xem ảnh đại diện to rõ nét\n"
        "`>info [@user]` — Xem thông tin chi tiết thành viên\n"
        "*(Bỏ trống @user để xem của chính mình)*"
    ), inline=False)
    p4.add_field(name="🧹 Dọn dẹp", value=(
        "`>clear [số]` — Xóa số lượng tin nhắn chỉ định\n"
        "*(Yêu cầu quyền Manage Messages)*"
    ), inline=False)
    p4.set_footer(text="Trang 4/5 — Tiện ích")
 
    # ---------- Trang 5: Quản trị ----------
    p5 = discord.Embed(title="⚙️ Quản trị", color=0x95a5a6)
    p5.add_field(name="📊 Thông tin", value=(
        "`>status` — Xem trạng thái bot (ping, uptime...)\n"
        "`>serverinfo` — Xem thông tin server hiện tại"
    ), inline=False)
    p5.add_field(name="🔧 Bảo trì", value=(
        "`>reset` — Reset kết nối âm thanh khi bị đơ/lỗi\n"
        "`>restart` — Khởi động lại bot *(chỉ Admin)*"
    ), inline=False)
    p5.add_field(name="⚠️ Lưu ý", value=(
        "`>restart` yêu cầu quyền **Administrator**\n"
        "Khi bot bị đơ nhạc: dùng `>reset` trước, rồi `>play` lại"
    ), inline=False)
    p5.set_footer(text="Trang 5/5 — Quản trị")
 
    return [p1, p2, p3, p4, p5]
 
 
# ==================== COG: UTILITY ====================
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setvoice(self, ctx, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        self.bot._say_channel = ch.id
        await ctx.send(f"✅ Kênh dùng lệnh >say: {ch.mention}", delete_after=5)
 
    @commands.command()
    async def say(self, ctx, *, text: str):
        say_ch = getattr(self.bot, '_say_channel', None)
        if not say_ch:
            return await ctx.send("❌ Chưa set kênh cho lệnh này. Vui lòng liên hệ Admin để cấu hình bot.", delete_after=10)
        if ctx.channel.id != say_ch:
            return
        try:
            await ctx.message.delete()
        except:
            pass
        if not ctx.author.voice:
            return await ctx.send(f"{ctx.author.mention} ❌ Bạn phải vào phòng Voice trước!", delete_after=5)
        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client
        if vc.is_playing():
            return await ctx.send(
                f"🚫 {ctx.author.mention} Bot đang bận phát nhạc! Vui lòng **dùng bot khác** để nói nhé!",
                delete_after=20
            )
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={encoded_text}&tl=vi"
        try:
            source = discord.FFmpegPCMAudio(url, before_options="-user_agent 'Mozilla/5.0'")
            vc.play(source)
            await ctx.send(f"🗣️ {ctx.author.mention} nói: **{text}**")
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}", delete_after=5)
 
    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        role = discord.utils.get(ctx.guild.roles, name="đệ của Đại Sư Tỷ")
        if not role or role not in ctx.author.roles:
            return await ctx.send("❌ Bạn không có quyền dùng lệnh này!", delete_after=5)
        member = member or ctx.author
        embed = discord.Embed(title=f"📸 Avatar của {member.display_name}", color=0x3498db)
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await ctx.send(embed=embed)
 
    @commands.command()
    async def info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"📄 Hồ sơ: {member.display_name}", color=member.color)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="🆔 ID",                value=member.id,                                inline=True)
        embed.add_field(name="📅 Ngày tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📥 Ngày vào Server",    value=member.joined_at.strftime("%d/%m/%Y"),  inline=True)
        embed.add_field(name="👑 Chức vụ cao nhất",   value=member.top_role.mention,                inline=True)
        await ctx.send(embed=embed)
 
    @commands.command()
    async def clear(self, ctx, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(f"❌ {ctx.author.mention} Bạn không có quyền xóa tin nhắn!", delete_after=5)
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"🧹 Đã dọn dẹp **{len(deleted) - 1}** tin nhắn!", delete_after=3)
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}", delete_after=5)
 
    @commands.command()
    async def help(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        pages = build_help_pages(self.bot)
        view  = HelpView(pages)
        view.message = await ctx.send(embed=pages[0], view=view)
 
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def chat(self, ctx, *, text: str):
        cmd_id = getattr(self.bot, '_chat_cmd_channel', None)
        out_id = getattr(self.bot, '_chat_out_channel', None)
        if cmd_id and ctx.channel.id != cmd_id:
            return
        if not out_id:
            return await ctx.send("❌ Chưa set kênh đích. Dùng `>setchatout #kênh`", delete_after=5)
        out_ch = ctx.guild.get_channel(out_id)
        if not out_ch:
            return await ctx.send("❌ Không tìm thấy kênh đích.", delete_after=5)
        await out_ch.send(text)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rep(self, ctx, message_id: int, *, text: str):
        out_id = getattr(self.bot, '_chat_out_channel', None)
        if not out_id:
            return await ctx.send("❌ Chưa set kênh đích. Dùng >setchatout #kênh", delete_after=5)
        out_ch = ctx.guild.get_channel(out_id)
        if not out_ch:
            return await ctx.send("❌ Không tìm thấy kênh đích.", delete_after=5)
        try:
            target_msg = await out_ch.fetch_message(message_id)
            await target_msg.reply(text)
        except discord.NotFound:
            await ctx.send("❌ Không tìm thấy tin nhắn với ID đó.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}", delete_after=5)
 
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchatin(self, ctx, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        self.bot._chat_cmd_channel = ch.id
        await ctx.send(f"✅ Kênh lệnh chat: {ch.mention}", delete_after=5)
 
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchatout(self, ctx, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        self.bot._chat_out_channel = ch.id
        await ctx.send(f"✅ Kênh đích chat: {ch.mention}", delete_after=5)
 
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def chatinfo(self, ctx):
        cmd_id = getattr(self.bot, '_chat_cmd_channel', None)
        out_id = getattr(self.bot, '_chat_out_channel', None)
        cmd_ch = ctx.guild.get_channel(cmd_id).mention if cmd_id else "Chưa set"
        out_ch = ctx.guild.get_channel(out_id).mention if out_id else "Chưa set"
        await ctx.send(f"📢 Kênh lệnh: {cmd_ch}\n📤 Kênh đích: {out_ch}", delete_after=10)
 
    @commands.command()
    async def afk(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ Bạn phải vào phòng voice trước!", delete_after=5)
        if getattr(self.bot, '_afk_owner', None):
            owner_id = self.bot._afk_owner
            if owner_id != ctx.author.id:
                owner = ctx.guild.get_member(owner_id)
                name = owner.display_name if owner else "người khác"
                return await ctx.send(f"❌ Bot đang được **{name}** dùng AFK rồi!", delete_after=5)
        if ctx.voice_client:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect(self_deaf=True)
        self.bot._afk_owner = ctx.author.id
        await ctx.send(f"😴 Bot đang AFK tại **{vc.channel.name}**. Dùng `>leave` để thoát.", delete_after=10)
        try:
            await ctx.message.delete()
        except:
            pass
 
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return
        if before.channel and not after.channel:
            if getattr(self.bot, '_afk_owner', None):
                self.bot._afk_owner = None
 
# ==================== SETUP ====================
async def setup(bot):
    await bot.add_cog(Utility(bot))

