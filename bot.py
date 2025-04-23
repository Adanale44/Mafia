import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from comandos.crear_partida import registrar_comandos_partida
from comandos.fase_noche import registrar_comandos_noche
from comandos.fase_dia import registrar_comandos_dia

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
partidas = {}

registrar_comandos_partida(bot, partidas)
registrar_comandos_noche(bot, partidas)
registrar_comandos_dia(bot, partidas)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

bot.run(TOKEN)
