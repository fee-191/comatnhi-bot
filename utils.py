import discord
import datetime

def format_time(ms):
    if not ms:
        return "0:00:00"
    seconds = int(ms) // 1000
    return str(datetime.timedelta(seconds=seconds))

def create_now_playing_embed(player, track):
    if not track:
        return discord.Embed(title="❌ Không có nhạc", color=0xe74c3c)
    embed = discord.Embed(color=0xff0000)
    embed.set_author(name="Đang phát 🎵", icon_url="https://i.imgur.com/SBMH84I.png")
    embed.title = track.title
    embed.url = track.uri
    if track.artwork:
        embed.set_image(url=track.artwork)
    embed.add_field(name="⏱️ Thời lượng", value=f"`{format_time(track.length)}`", inline=True)
    embed.add_field(name="📡 Nguồn",      value=f"`{track.source}`",               inline=True)
    embed.add_field(name="🔊 Volume",     value=f"**{player.volume}%**",            inline=True)
    if player.loop:
        loop_status = "🔂 Bài này"
    elif player.loop_queue:
        loop_status = "🔁 Cả queue"
    else:
        loop_status = "❌ Tắt"
    embed.add_field(name="🔄 Loop",      value=loop_status,                         inline=True)
    embed.add_field(name="📋 Hàng chờ", value=f"**{len(player.queue)} bài**",       inline=True)
    embed.add_field(name="\u200b",       value="\u200b",                             inline=True)
    if player.queue:
        upcoming = player.queue[:3]
        next_list = ""
        for i, t in enumerate(upcoming, 1):
            next_list += f"`{i}.` {t.title} — `{format_time(t.length)}`\n"
        if len(player.queue) > 3:
            next_list += f"*... và {len(player.queue) - 3} bài nữa — xem 📋*"
        embed.add_field(name="⏭️ Tiếp theo", value=next_list, inline=False)
    embed.set_footer(text="🎵 Đang phát | Bấm 📋 để quản lý hàng chờ")
    return embed

def create_queue_embed(player):
    embed = discord.Embed(title="📋 Hàng chờ phát nhạc", color=0x9b59b6)
    if player.current:
        loop_icon = "🔂" if player.loop else ("🔁" if player.loop_queue else "▶️")
        embed.add_field(
            name=f"{loop_icon} Đang phát",
            value=f"**{player.current.title}** — `{format_time(player.current.length)}`",
            inline=False
        )
    if player.queue:
        desc = ""
        for i, t in enumerate(player.queue[:15], 1):
            desc += f"`{i}.` {t.title} — `{format_time(t.length)}`\n"
        if len(player.queue) > 15:
            desc += f"\n*... và {len(player.queue) - 15} bài nữa*"
        embed.add_field(
            name=f"📝 Hàng chờ ({len(player.queue)} bài)",
            value=desc, inline=False
        )
    else:
        embed.add_field(name="📝 Hàng chờ", value="*Trống — thêm bài bằng `>play`*", inline=False)
    embed.set_footer(text="🗑️ Chọn bài từ menu để xóa | Bấm 🎵 để quay lại")
    return embed
