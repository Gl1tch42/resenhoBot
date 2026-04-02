import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from tasks.task_update_data import atualizar_arquivo
import json

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
    tasks.start()
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


@tasks.loop(seconds=120)
async def tasks():
    atualizar_arquivo()
    print("Estou funcionando!")

@bot.command()
async def jogos(ctx):
    await ctx.send("⏳ Buscando jogos da rodada... aguarde.")
    
    with open('data\dados_jogos.json', 'r', encoding='utf-8') as f:
      jogos = json.load(f)
    
    if not jogos:
        return await ctx.send("Não consegui encontrar jogos no momento.")

    mensagem = "**BR Brasileirão — Regular Season**\n\n"
    
    for j in jogos:
        # Lógica de ícones baseada no status
        if "Encerrado" in j['status'] or "Ontem" in j['status']:
            emoji = "⬛"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']})"
        elif "’" in j['status'] or "Intervalo" in j['status']: # Se tem o símbolo de minutos 67'
            emoji = "🟢"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']}) ⬅️ *ao vivo*"
        else: # Jogos futuros
            emoji = "🔵"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']})"
            
        mensagem += linha + "\n\n"

    await ctx.send(mensagem)

# Substitua pelo Token que você pegou no Developer Portal
bot.run(DISCORD_TOKEN)