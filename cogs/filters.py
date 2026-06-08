import discord
from discord.ext import commands

# ==================== COG: FILTERS ====================
class Filters(commands.Cog):
    """🎛️ Hiệu ứng âm thanh nâng cao
    
    File này dành cho các filter âm thanh mở rộng trong tương lai.
    Hiện tại tốc độ phát đã được tích hợp vào MusicController (nút menu trong panel).
    
    Ví dụ các tính năng có thể thêm sau:
    - !bass [0-5]     → Tăng/giảm bass
    - !nightcore      → Hiệu ứng nightcore
    - !vaporwave      → Hiệu ứng vaporwave
    - !treble [0-5]   → Tăng/giảm treble
    - !karaoke        → Lọc giọng
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bass(self, ctx, level: int = 3):
        """Tăng bass: !bass [0-5] (mặc định: 3)"""
        vc = ctx.voice_client
        if not vc or not vc.current:
            return await ctx.send("❌ Chưa có nhạc đang phát.", delete_after=5)
        if not 0 <= level <= 5:
            return await ctx.send("❌ Mức bass phải từ 0 đến 5.", delete_after=5)

        filters: wavelink.Filters = vc.filters
        # Tăng bass bằng equalizer (band 0-2 là tần số bass)
        boost = level * 0.1
        filters.equalizer.set(bands=[
            {"band": 0, "gain": boost},
            {"band": 1, "gain": boost},
            {"band": 2, "gain": boost * 0.75},
        ])
        await vc.set_filters(filters)
        await ctx.send(f"🔈 Bass: **{level}/5**", delete_after=5)

    @commands.command()
    async def nightcore(self, ctx):
        """Bật/tắt hiệu ứng Nightcore (tăng pitch + tốc độ)"""
        vc = ctx.voice_client
        if not vc or not vc.current:
            return await ctx.send("❌ Chưa có nhạc đang phát.", delete_after=5)

        filters: wavelink.Filters = vc.filters
        # Kiểm tra xem nightcore đang bật chưa
        if not getattr(vc, "nightcore_on", False):
            filters.timescale.set(speed=1.2, pitch=1.3, rate=1.0)
            vc.nightcore_on = True
            await ctx.send("🌙 **Nightcore** đã bật!", delete_after=5)
        else:
            filters.reset()
            vc.nightcore_on = False
            await ctx.send("🌙 **Nightcore** đã tắt.", delete_after=5)
        await vc.set_filters(filters)

    @commands.command()
    async def resetfilter(self, ctx):
        """Reset tất cả filter về mặc định"""
        vc = ctx.voice_client
        if not vc:
            return await ctx.send("❌ Bot chưa ở trong phòng.", delete_after=5)
        filters: wavelink.Filters = vc.filters
        filters.reset()
        await vc.set_filters(filters)
        vc.nightcore_on = False
        await ctx.send("🔄 Đã reset tất cả filter về mặc định.", delete_after=5)

# ==================== SETUP ====================
async def setup(bot):
    await bot.add_cog(Filters(bot))
