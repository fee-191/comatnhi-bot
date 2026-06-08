import discord
import os
import time
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='>', intents=intents, help_command=None)
bot.start_time = time.time()

COGS = ["cogs.music", "cogs.filters", "cogs.utility", "cogs.admin", "cogs.minigame"]

async def setup_hook():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f'  ✅ Loaded: {cog}')
        except Exception as e:
            print(f'  ❌ Lỗi load {cog}: {e}')

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Online!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu tham số! Dùng `>help` để xem cách dùng.", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Sai định dạng tham số!", delete_after=5)
    else:
        print(f'❌ [{ctx.command}]: {error}')

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Không tìm thấy DISCORD_TOKEN!")
