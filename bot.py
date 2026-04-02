import discord
from discord.ext import commands
from discord.ext import tasks
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
 
load_dotenv()
 
# ============================================================
# CONFIGURAÇÕES
# ============================================================
DISCORD_TOKEN      = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID   = int(os.getenv("ALERT_CHANNEL_ID", "0"))
FOOTBALL_API_KEY   = os.getenv("FOOTBALL_API_KEY")
 
# Times que você NÃO GOSTA — o bot avisa quando estão sofrendo
RIVAL_TEAMS = [
    "Flamengo",
    "Palmeiras",
    # Adicione mais aqui
]
 
# IDs de ligas monitoradas (API-Football)
# 71 = Brasileirão A | 72 = Série B | 73 = Copa do Brasil
# 2 = Champions | 13 = Libertadores | 11 = Sul-Americana
LEAGUE_IDS = [71, 72, 73]
 
# Intervalo de verificação em segundos
CHECK_INTERVAL = 60

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Sucesso! Bot conectado como: {bot.user.name}')

@bot.command()
async def salve(ctx):
    await ctx.send(f'Salve, {ctx.author.mention}! Tudo tranquilo?')

# Substitua pelo Token que você pegou no Developer Portal
bot.run(DISCORD_TOKEN)