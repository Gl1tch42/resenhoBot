import discord
from discord.ext import commands, tasks
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
 
load_dotenv()
 
# ============================================================
# CONFIGURAÇÕES
# ============================================================
DISCORD_TOKEN      = os.getenv("DISCORD_TOKEN", "")
ALERT_CHANNEL_ID   = int(os.getenv("ALERT_CHANNEL_ID", "0"))
FOOTBALL_API_KEY   = os.getenv("FOOTBALL_API_KEY", "")
 
# Times que você NÃO GOSTA — o bot avisa quando estão sofrendo
RIVAL_TEAMS = [
    "Palmeiras",
    "vasco da gama",
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
    printer.start()
    print(f'Sucesso! Bot conectado como: {bot.user.name}')

@bot.command()
async def salve(ctx):
    await ctx.send(f'Salve, {ctx.author.mention}! Tudo tranquilo?')

@bot.command()
async def ajuda(ctx):
    help_text = (
        "Olá! Eu sou o ResenhoBot, seu assistente para acompanhar os jogos dos seus times rivais!\n\n"
        "Comandos disponíveis:\n"
        "`!salve` - Receba uma saudação personalizada.\n"
        "`!ajuda` - Veja esta mensagem de ajuda.\n\n"
        "Eu monitoro os jogos ao vivo dos times que você não gosta e aviso quando eles estão sofrendo! Fique ligado!"
    )
    await ctx.send(help_text)

    """Busca jogos do Brasileirão dentro da janela permitida (Abril 2026)"""
    url = "https://v3.football.api-sports.io/fixtures"
    
    # Pegando a data de hoje formatada exatamente como a API sugeriu
    hoje = "2026-04-02" 
    
    params = {
        "league": "71",   # Brasileirão Série A
        "season": "2026", # Agora vamos usar 2026!
        "date": hoje
    }
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': FOOTBALL_API_KEY
    }

    await ctx.send(f"⚽ Buscando jogos de hoje ({hoje}) no Brasileirão 2026...")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            data = await resp.json()
            
            # Verificação de erro de permissão caso a API mude de ideia
            if data.get("errors"):
                erro_msg = data["errors"]
                return await ctx.send(f"⚠️ Erro da API: {erro_msg}")

            fixtures = data.get('response', [])

            if not fixtures:
                return await ctx.send(f"📅 Não encontrei jogos para o dia {hoje}. Tente `!jogos_amanha`.")

            embed = discord.Embed(
                title=f"🏟️ Rodada - {hoje}",
                description="Brasileirão Série A 2026",
                color=discord.Color.green()
            )

            for game in fixtures:
                home = game['teams']['home']['name']
                away = game['teams']['away']['name']
                
                # Placar (pode ser None se o jogo não começou)
                gol_h = game['goals']['home'] if game['goals']['home'] is not None else "-"
                gol_a = game['goals']['away'] if game['goals']['away'] is not None else "-"
                
                status = game['fixture']['status']['short'] # Ex: FT (Finalizado), NS (Não começou)
                
                # Lógica de Rivais
                emoji_zoeira = ""
                if home in RIVAL_TEAMS and isinstance(gol_h, int) and gol_h < gol_a:
                    emoji_zoeira = " 😂"
                elif away in RIVAL_TEAMS and isinstance(gol_a, int) and gol_a < gol_h:
                    emoji_zoeira = " 😂"

                embed.add_field(
                    name=f"{home} {gol_h} x {gol_a} {away}",
                    value=f"Status: {status}{emoji_zoeira}",
                    inline=False
                )

            await ctx.send(embed=embed)

@tasks.loop(seconds=120)
async def printer():
    print("Estou funcionando!")

    """Formata uma linha de jogo com status, placar e horário."""
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    status_short = f["fixture"]["status"]["short"]
    elapsed = f["fixture"]["status"].get("elapsed")
    home_g = f["goals"]["home"]
    away_g = f["goals"]["away"]
 
    # Jogo ao vivo
    if status_short in ("1H", "2H", "HT", "ET", "P"):
        min_str = f"{elapsed}'" if elapsed else "?"
        return f"🟢 **{home} {home_g} x {away_g} {away}** — {min_str}"
 
    # Encerrado
    if status_short == "FT":
        return f"⬛ ~~{home}~~ {home_g} x {away_g} {away} *(encerrado)*"
 
    # Agendado — mostra horário local (UTC-3)
    import datetime
    ts = f["fixture"].get("timestamp")
    if ts:
        dt = datetime.datetime.utcfromtimestamp(ts) - datetime.timedelta(hours=3)
        hora = dt.strftime("%d/%m %H:%M")
    else:
        hora = "?"
    return f"🔵 {home} x {away} — {hora}"
# Substitua pelo Token que você pegou no Developer Portal
bot.run(DISCORD_TOKEN)