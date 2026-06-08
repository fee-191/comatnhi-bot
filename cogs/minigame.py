import discord
import csv
import json
import os
import re
import asyncio
from discord.ext import commands
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'minigame.json')
REGISTER_PATTERN = re.compile(r'^Lucky\s*Player\s*[-\u2013]\s*(\d+)\s*[-\u2013]\s*(.+)$', re.IGNORECASE)

def load_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {"channel_id": None, "registrations": {}}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Minigame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cache = None
        self._lock = asyncio.Lock()

    def _get_data(self):
        if self._cache is None:
            self._cache = load_data()
        return self._cache

    def _save(self):
        if self._cache is not None:
            save_data(self._cache)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        async with self._lock:
            data = self._get_data()
            if not data["channel_id"] or message.channel.id != data["channel_id"]:
                return

            match = REGISTER_PATTERN.match(message.content.strip())
            if not match:
                await message.add_reaction("❌")
                await message.reply(
                    "Wrong registration format! [Sai cu phap dang ky!]\n"
                    "Correct format [Cu phap dung]: Lucky Player - {ID} - {Name/Ten}\n"
                    "Example [Vi du]: Lucky Player - 000000001 - A O"
                )
                return

            game_id = match.group(1).strip()
            game_name = match.group(2).strip()
            discord_id = str(message.author.id)
            registrations = data.get("registrations", {})

            # Case: đăng ký y hệt
            old_entry = registrations.get(discord_id)
            if old_entry and old_entry["game_id"] == game_id and old_entry["game_name"] == game_name:
                await message.add_reaction("✅")
                await message.reply(
                    "You have already registered correctly! [Ban da dang ky dung roi!]\n"
                    "ID: `" + game_id + "` | Name [Ten]: `" + game_name + "`"
                )
                return

            # Case: ID đã được người khác đăng ký
            for uid, entry in registrations.items():
                if uid != discord_id and entry["game_id"] == game_id:
                    await message.add_reaction("❌")
                    await message.reply(
                        "ID `" + game_id + "` has already been registered by someone else! "
                        "[ID nay da duoc nguoi khac dang ky roi!]"
                    )
                    return

            is_update = old_entry is not None

            # Thả ❌ vào tin nhắn cũ
            if is_update and old_entry.get("message_id"):
                try:
                    old_msg = await message.channel.fetch_message(int(old_entry["message_id"]))
                    await old_msg.add_reaction("❌")
                    try:
                        await old_msg.remove_reaction("✅", self.bot.user)
                    except:
                        pass
                except:
                    pass

            # Lưu đăng ký
            registrations[discord_id] = {
                "discord_id": discord_id,
                "discord_name": str(message.author),
                "game_id": game_id,
                "game_name": game_name,
                "timestamp": message.created_at.isoformat(),
                "message_id": str(message.id)
            }
            data["registrations"] = registrations
            self._save()

        # Cấp role (ngoài lock để không block)
        role = discord.utils.get(message.guild.roles, name="LuckyPlayer")
        if role:
            try:
                await message.author.add_roles(role)
            except Exception as e:
                print(f"Cannot assign role: {e}")

        await message.add_reaction("✅")

        if is_update:
            await message.reply(
                "Registration updated! [Da cap nhat dang ky!]\n"
                "New ID [ID moi]: `" + game_id + "` | New name [Ten moi]: `" + game_name + "`"
            )
        else:
            await message.reply(
                "Registration successful! [Dang ky thanh cong!]\n"
                "ID: `" + game_id + "` | Name [Ten]: `" + game_name + "`"
            )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        async with self._lock:
            data = self._get_data()
            old_channel_id = data.get("channel_id")
            data["channel_id"] = ch.id
            self._save()
        if old_channel_id and old_channel_id != ch.id:
            old_ch = ctx.guild.get_channel(old_channel_id)
            old_name = old_ch.mention if old_ch else f"`{old_channel_id}`"
            await ctx.send(f"✅ Da doi kenh dang ky tu {old_name} sang {ch.mention}")
        else:
            await ctx.send(f"✅ Da set kenh dang ky: {ch.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def channelinfo(self, ctx):
        data = self._get_data()
        ch_id = data.get("channel_id")
        if not ch_id:
            return await ctx.send("Chua set kenh dang ky. Dung !setchannel #kenh")
        ch = ctx.guild.get_channel(ch_id)
        name = ch.mention if ch else f"`{ch_id}`"
        await ctx.send(f"Kenh dang ky hien tai: {name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def exportcsv(self, ctx):
        data = self._get_data()
        registrations = data.get("registrations", {})
        if not registrations:
            return await ctx.send("Chua co ai dang ky.")

        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'lucky_players.csv')
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['ma_so', 'ten_kh'])
            writer.writeheader()
            for entry in sorted(registrations.values(), key=lambda x: x['timestamp']):
                writer.writerow({
                    'ma_so': entry['game_id'],
                    'ten_kh': entry['game_name']
                })

        await ctx.send(
            f"Danh sach {len(registrations)} nguoi dang ky:",
            file=discord.File(csv_path, filename=f"lucky_players_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listplayers(self, ctx):
        data = self._get_data()
        registrations = data.get("registrations", {})
        if not registrations:
            return await ctx.send("Chua co ai dang ky.")
        embed = discord.Embed(title=f"Lucky Players — {len(registrations)} nguoi", color=0xf1c40f)
        entries = sorted(registrations.values(), key=lambda x: x['timestamp'])
        desc = ""
        for i, e in enumerate(entries[:20], 1):
            desc += f"`{i}.` **{e['game_name']}** | ID: `{e['game_id']}` | <@{e['discord_id']}>\n"
        if len(entries) > 20:
            desc += f"\n_...va {len(entries) - 20} nguoi nua. Dung !exportcsv de xem day du._"
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeplayer(self, ctx, member: discord.Member):
        async with self._lock:
            data = self._get_data()
            discord_id = str(member.id)
            if discord_id not in data.get("registrations", {}):
                return await ctx.send(f"{member.mention} chua dang ky.")
            entry = data["registrations"].pop(discord_id)
            self._save()

        role = discord.utils.get(ctx.guild.roles, name="LuckyPlayer")
        if role and role in member.roles:
            try:
                await member.remove_roles(role)
            except:
                pass

        if entry.get("message_id") and data.get("channel_id"):
            ch = ctx.guild.get_channel(data["channel_id"])
            if ch:
                try:
                    old_msg = await ch.fetch_message(int(entry["message_id"]))
                    await old_msg.add_reaction("❌")
                    try:
                        await old_msg.remove_reaction("✅", self.bot.user)
                    except:
                        pass
                except:
                    pass

        await ctx.send(
            f"Da xoa dang ky cua {member.mention} | "
            f"ID: `{entry['game_id']}` | Ten: `{entry['game_name']}`"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetminigame(self, ctx):
        async with self._lock:
            data = self._get_data()
            count = len(data.get("registrations", {}))
            data["registrations"] = {}
            self._save()

        role = discord.utils.get(ctx.guild.roles, name="LuckyPlayer")
        if role:
            for member in role.members:
                try:
                    await member.remove_roles(role)
                except:
                    pass

        await ctx.send(f"Da reset xong! Xoa {count} dang ky va thu hoi role khoi tat ca.")

    @commands.command()
    async def mystatus(self, ctx):
        data = self._get_data()
        entry = data.get("registrations", {}).get(str(ctx.author.id))
        if not entry:
            return await ctx.send(
                "You have not registered yet. [Ban chua dang ky.]\n"
                "Format: Lucky Player - {ID} - {Name/Ten}",
                delete_after=15
            )
        await ctx.send(
            "You are registered! [Ban da dang ky!]\n"
            "ID: `" + entry['game_id'] + "` | Name [Ten]: `" + entry['game_name'] + "`",
            delete_after=15
        )

async def setup(bot):
    await bot.add_cog(Minigame(bot))
