import discord
import os
import time
from discord.ext import commands

def format_uptime(seconds: float) -> str:
    seconds = int(seconds)
    days    = seconds // 86400
    hours   = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs    = seconds % 60
    parts = []
    if days:    parts.append(f"{days} ngày")
    if hours:   parts.append(f"{hours} giờ")
    if minutes: parts.append(f"{minutes} phút")
    if secs:    parts.append(f"{secs} giây")
    return " ".join(parts) if parts else "Vừa khởi động"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        ping = round(self.bot.latency * 1000)
        ping_icon = "🟢" if ping < 80 else ("🟡" if ping < 150 else "🔴")
        uptime = format_uptime(time.time() - self.bot.start_time)

        # Đếm số bot đang phát nhạc
        playing_count = sum(
            1 for vc in self.bot.voice_clients
            if vc.is_playing()
        )

        embed = discord.Embed(
            title="🤖 Trạng thái Bot",
            color=0x2ecc71 if ping < 150 else 0xe74c3c
        )
        embed.add_field(name="📶 Ping",           value=f"{ping_icon} **{ping}ms**",                        inline=True)
        embed.add_field(name="⏱️ Uptime",          value=f"**{uptime}**",                                    inline=True)
        embed.add_field(name="🎵 Đang phát",       value=f"**{playing_count}** server",                      inline=True)
        embed.add_field(name="🏠 Tổng server",     value=f"**{len(self.bot.guilds)}** server",               inline=True)
        embed.add_field(name="👥 Tổng thành viên", value=f"**{sum(g.member_count for g in self.bot.guilds)}** người", inline=True)
        embed.set_footer(text=f"Bot: {self.bot.user.name}")
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command()
    async def reset(self, ctx):
        if ctx.voice_client:
            try:
                await ctx.voice_client.stop()
                await ctx.voice_client.disconnect(force=True)
                await ctx.send("🔄 Đã reset kết nối! Thử `>join` hoặc `>play` lại nhé.", delete_after=10)
            except Exception as e:
                await ctx.send(f"⚠️ Lỗi reset: {e}", delete_after=5)
        else:
            await ctx.send("❓ Bot không ở trong phòng, không thể reset!", delete_after=5)

    @commands.command()
    async def restart(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Không có quyền! Chỉ Admin mới được dùng lệnh này.", delete_after=5)
        await ctx.send("👋 Đang khởi động lại hệ thống... (Vui lòng đợi ~15s)", delete_after=10)
        os.system("systemctl restart discordbot4")

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"🏠 {guild.name}", color=0x2ecc71)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="🆔 ID",         value=guild.id,                              inline=True)
        embed.add_field(name="👑 Chủ server", value=guild.owner.mention,                   inline=True)
        embed.add_field(name="👥 Thành viên", value=guild.member_count,                    inline=True)
        embed.add_field(name="📅 Ngày tạo",   value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="💬 Kênh text",  value=len(guild.text_channels),              inline=True)
        embed.add_field(name="🔊 Kênh voice", value=len(guild.voice_channels),             inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
