import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from tasks.task_update_data import atualizar_arquivo
from functions.task_monitor_resenha import verificar_resenha
import json
import asyncio

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
    "Santos",
    "Atlético-MG",
    "Fluminense",
    "Flamengo",
    # Adicione mais aqui
]
 
# Intervalo de verificação em segundos
CHECK_INTERVAL = 60

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    if not tasks.is_running():
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
        if "ENCERRADO" in j['tipo_status'] or "CANCELADO" in j['tipo_status'] or "ADIADO" in j['tipo_status']:
            emoji = "⬛"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']})"
        elif "AO_VIVO" in j['tipo_status']: # Se tem o símbolo de minutos 67'
            emoji = "🟢"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']}) ⬅️ *ao vivo*"
        else: # Jogos futuros
            emoji = "🔵"
            linha = f"{emoji} {j['mandante']} {j['placar']} {j['visitante']} ({j['status']})"
            
        mensagem += linha + "\n\n"

    await ctx.send(mensagem)

@tasks.loop(seconds=CHECK_INTERVAL)
async def tasks():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, atualizar_arquivo)
    await verificar_resenha(
        bot=bot,
        alert_channel_id=ALERT_CHANNEL_ID,
        rival_teams=RIVAL_TEAMS,
    )


# Substitua pelo Token que você pegou no Developer Portal
bot.run(DISCORD_TOKEN)