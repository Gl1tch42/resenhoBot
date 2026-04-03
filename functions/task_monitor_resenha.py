import json
import os
import discord
from datetime import datetime

# Caminho do arquivo gerado pelo Selenium
DATA_PATH = r'data\dados_jogos.json'

# Estado anterior dos jogos: chave = "mandante_visitante", valor = dict com situação e placar
_estado_anterior: dict[str, dict] = {}

SIT_LABEL = {
    "winning": "VENCENDO  ✅",
    "drawing":  "EMPATANDO ⚠️",
    "losing":   "PERDENDO  🚨",
}

def _log(tag: str, msg: str) -> None:
    hora = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora}] [{tag}] {msg}")


def _is_rival(team_name: str, rival_teams: list[str]) -> bool:
    name = team_name.lower().strip()
    return any(r.lower().strip() in name or name in r.lower().strip() for r in rival_teams)


def _parse_placar(placar: str) -> tuple[int, int] | None:
    """
    Converte '2 x 1' em (2, 1).
    Retorna None se o placar for 'x' (jogo ainda não começou).
    """
    partes = placar.strip().split("x")
    if len(partes) != 2:
        return None
    try:
        return int(partes[0].strip()), int(partes[1].strip())
    except ValueError:
        return None  # placar = "x" — jogo não iniciado


def _is_live(jogo: dict) -> bool:
    return jogo.get("tipo_status", "").upper() == "AO_VIVO"


def _is_finished(jogo: dict) -> bool:
    return jogo.get("tipo_status", "").upper() == "ENCERRADO"


def _is_future(jogo: dict) -> bool:
    return jogo.get("tipo_status", "").upper() == "FUTURO"


def _situacao_rival(placar: tuple[int, int], rival_is_home: bool) -> str:
    """Retorna 'winning', 'drawing' ou 'losing' do ponto de vista do rival."""
    rival_g = placar[0] if rival_is_home else placar[1]
    opp_g   = placar[1] if rival_is_home else placar[0]
    if rival_g > opp_g:
        return "winning"
    if rival_g == opp_g:
        return "drawing"
    return "losing"


def _chave(jogo: dict) -> str:
    return f"{jogo['mandante'].strip().lower()}_{jogo['visitante'].strip().lower()}"


async def verificar_resenha(bot: discord.ext.commands.Bot, alert_channel_id: int, rival_teams: list[str]) -> None:
    """
    Lê dados_jogos.json, compara com estado anterior e envia alertas
    apenas quando a situação do rival muda.
    Deve ser chamada dentro de um loop periódico (tasks.loop).
    """
    print("🔍 [Resenha] Verificando jogos para possíveis resenhas...")
    global _estado_anterior

    _log("MONITOR", "=" * 55)
    _log("MONITOR", "Iniciando ciclo de monitoramento...")

    # ── Lê o arquivo ────────────────────────────────────────────
    try:
        if not os.path.exists(DATA_PATH):
            _log("ERRO", f"Arquivo não encontrado: {DATA_PATH}")
            return

        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            jogos: list[dict] = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _log("ERRO", f"Falha ao ler JSON: {e}")
        return

    _log("MONITOR", f"JSON carregado — {len(jogos)} jogo(s) encontrado(s)")

    channel = bot.get_channel(alert_channel_id)
    if channel is None:
        _log("ERRO", f"Canal Discord não encontrado (ID: {alert_channel_id})")
        return

    # Contadores do ciclo
    ignorados    = 0
    ao_vivo      = 0
    sem_rival    = 0
    monitorados  = 0
    sem_mudanca  = 0
    alertas      = 0

    for jogo in jogos:
        mandante   = jogo.get("mandante", "").strip()
        visitante  = jogo.get("visitante", "").strip()
        placar_str = jogo.get("placar", "").strip()
        status     = jogo.get("status", "").strip()
        partida    = f"{mandante} x {visitante}"

        # Descarta encerrados
        if _is_finished(jogo):
            _log("SKIP", f"{partida} — encerrado")
            ignorados += 1
            continue

        if _is_future(jogo):
            _log("SKIP", f"{partida} — ainda não iniciou")
            ignorados += 1
            continue

        placar = _parse_placar(placar_str)
        if placar is None:
            _log("SKIP", f"{partida} — placar inválido")
            ignorados += 1
            continue

        ao_vivo += 1

        # Verifica se tem rival
        rival_is_home = _is_rival(mandante, rival_teams)
        rival_is_away = _is_rival(visitante, rival_teams)

        if not rival_is_home and not rival_is_away:
            _log("INFO", f"{partida} [{placar_str}] — sem rival, ignorando")
            sem_rival += 1
            continue

        if rival_is_home and rival_is_away:
            _log("INFO", f"{partida} — ambos rivais, ignorando")
            sem_rival += 1
            continue

        monitorados += 1
        rival    = mandante if rival_is_home else visitante
        opponent = visitante if rival_is_home else mandante

        sit_atual   = _situacao_rival(placar, rival_is_home)
        chave       = _chave(jogo)
        anterior    = _estado_anterior.get(chave, {})
        sit_prev    = anterior.get("sit")
        placar_prev = anterior.get("placar")

        sit_prev_label = SIT_LABEL.get(sit_prev, "NOVO JOGO  🆕")
        sit_atual_label = SIT_LABEL[sit_atual]

        _log("RIVAL", f"{rival} | {placar_str} | {sit_prev_label} → {sit_atual_label}")

        situacao_mudou = sit_atual != sit_prev
        placar_mudou   = placar_str != placar_prev

        if not situacao_mudou and not (placar_mudou and sit_atual in ("losing", "drawing")):
            _log("OK", f"{rival} — sem mudança, nenhum alerta enviado")
            sem_mudanca += 1
            _estado_anterior[chave] = {"sit": sit_atual, "placar": placar_str}
            continue

        # ── ALERTA: rival começou a perder ou empatou saindo de vitória ──
        if sit_atual in ("losing", "drawing") and sit_prev == "winning":
            if sit_atual == "losing":
                descricao = f"😂 **{rival}** está **PERDENDO** para **{opponent}**!"
            else:
                descricao = f"😬 **{rival}** **EMPATOU** com **{opponent}**!"

            embed = discord.Embed(
                title="🚨 POSSÍVEL RESENHA! 🚨",
                description=(
                    f"@everyone\n\n"
                    f"{descricao}\n\n"
                    f"⚔️ **{mandante} {placar_str} {visitante}**\n"
                    f"📍 {status}"
                ),
                color=0xFF4444,
            )
            embed.set_footer(text="Brasileirão • ao vivo")
            await channel.send(content="@everyone", embed=embed)
            _log("ALERTA", f"🚨 RESENHA enviada! {rival} {sit_atual_label} | {placar_str}")
            alertas += 1

        # ── ALERTA: rival entrou ao vivo já perdendo/empatando ──────────
        elif sit_atual in ("losing", "drawing") and sit_prev is None:
            if sit_atual == "losing":
                descricao = f"😂 **{rival}** já está **PERDENDO** para **{opponent}**!"
            else:
                descricao = f"😬 **{rival}** começa **EMPATANDO** com **{opponent}**."

            embed = discord.Embed(
                title="🚨 POSSÍVEL RESENHA! 🚨",
                description=(
                    f"@everyone\n\n"
                    f"{descricao}\n\n"
                    f"⚔️ **{mandante} {placar_str} {visitante}**\n"
                    f"📍 {status}"
                ),
                color=0xFF4444,
            )
            embed.set_footer(text="Brasileirão • ao vivo")
            await channel.send(content="@everyone", embed=embed)
            _log("ALERTA", f"🚨 RESENHA (início detectado) | {rival} {sit_atual_label} | {placar_str}")
            alertas += 1

        # ── ALERTA: rival virou o jogo ───────────────────────────────────
        elif sit_atual == "winning" and sit_prev in ("losing", "drawing"):
            embed = discord.Embed(
                title="✅ RESENHA CANCELADA",
                description=(
                    f"@everyone\n\n"
                    f"😒 **{rival}** virou o jogo contra **{opponent}**. Acabou a festa.\n\n"
                    f"⚔️ **{mandante} {placar_str} {visitante}**\n"
                    f"📍 {status}"
                ),
                color=0x44BB44,
            )
            embed.set_footer(text="Brasileirão • ao vivo")
            await channel.send(content="@everyone", embed=embed)
            _log("ALERTA", f"✅ RESENHA CANCELADA | {rival} virou | {placar_str}")
            alertas += 1

        # ── Placar mudou, rival continua sofrendo ────────────────────────
        elif sit_atual in ("losing", "drawing") and placar_mudou and sit_prev in ("losing", "drawing"):
            if sit_atual == "losing":
                descricao = f"😂 **{rival}** continua **PERDENDO** — tomou mais um!"
            else:
                descricao = f"😬 **{rival}** segue **EMPATADO** com **{opponent}**."

            embed = discord.Embed(
                title="🚨 RESENHA CONTINUA! 🚨",
                description=(
                    f"@everyone\n\n"
                    f"{descricao}\n\n"
                    f"⚔️ **{mandante} {placar_str} {visitante}**\n"
                    f"📍 {status}"
                ),
                color=0xFF8800,
            )
            embed.set_footer(text="Brasileirão • ao vivo")
            await channel.send(content="@everyone", embed=embed)
            _log("ALERTA", f"🔥 RESENHA CONTINUA | {rival} | {placar_prev} → {placar_str}")
            alertas += 1

        # Atualiza estado
        _estado_anterior[chave] = {"sit": sit_atual, "placar": placar_str}

    # ── Limpa jogos encerrados do estado ────────────────────────
    chaves_ativas = {
        _chave(j) for j in jogos
        if _is_live(j) and _parse_placar(j.get("placar", "")) is not None
    }
    removidos = []
    for chave in list(_estado_anterior.keys()):
        if chave not in chaves_ativas:
            _estado_anterior.pop(chave, None)
            removidos.append(chave)

    if removidos:
        _log("CLEANUP", f"Removido(s) do estado: {', '.join(removidos)}")

    # ── Resumo do ciclo ──────────────────────────────────────────
    _log("RESUMO", f"Total: {len(jogos)} | Ignorados: {ignorados} | Ao vivo: {ao_vivo} | "
                   f"Sem rival: {sem_rival} | Monitorados: {monitorados} | "
                   f"Sem mudança: {sem_mudanca} | Alertas: {alertas}")
    _log("MONITOR", "Ciclo finalizado.")
    _log("MONITOR", "=" * 55)