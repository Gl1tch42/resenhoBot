# ⚽ Resenha Alert Bot — Python

### Instalar e rodar

```bash
# 1. Entre na pasta do projeto
cd resenhoBot

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# execução padrao sem ambiente virtual
python bot.py

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com seus dados
```

---

## Configuração passo a passo

### 1. Criar o bot no Discord

1. Acesse [discord.com/developers/applications](https://discord.com/developers/applications)
2. Clique em **New Application** → dê um nome (ex: `Resenha Alert`)
3. Vá em **Bot** → clique em **Add Bot**
4. Em **Privileged Gateway Intents**, ative:
   - `Server Members Intent`
   - `Message Content Intent`
5. Clique em **Reset Token** e copie → este é o `DISCORD_TOKEN`
6. Vá em **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Permissões: `Send Messages`, `Embed Links`, `Mention Everyone`
7. Acesse a URL gerada no navegador para adicionar o bot ao servidor

### 2. Obter a chave da API de futebol

1. Crie conta em [dashboard.api-football.com](https://dashboard.api-football.com/register)
2. Copie sua **API Key** → este é o `FOOTBALL_API_KEY`

### 3. Pegar o ID do canal

1. No Discord: **Configurações → Avançado → ativar Modo Desenvolvedor**
2. Clique com botão direito no canal de alertas → **Copiar ID**
3. Este é o `ALERT_CHANNEL_ID`

### 4. Configurar os times rivais

Abra o `bot.py` e edite a lista `RIVAL_TEAMS`:

```python
RIVAL_TEAMS = [
    "Flamengo",
    "Palmeiras",
    "São Paulo",
    # Adicione os times que você não gosta
]
```

> Os nomes devem ser parecidos com os que aparecem na API. A busca é por correspondência parcial, então `"Flamengo"` vai casar com `"Flamengo RJ"` ou `"CR Flamengo"`.

### 5. Configurar as ligas monitoradas (opcional)

```python
LEAGUE_IDS = [71, 72, 73]  # Brasileirão A, B e Copa do Brasil
```

| Liga | ID |
|------|-----|
| Brasileirão Série A | 71 |
| Brasileirão Série B | 72 |
| Copa do Brasil | 73 |
| Libertadores | 13 |
| Sul-Americana | 11 |
| Champions League | 2 |
| Europa League | 3 |
| Premier League | 39 |
| La Liga | 140 |

---

## Rodando o bot

```bash
python bot.py
```

Você deve ver no terminal:

```
✅ Bot online: ResenhaAlert#1234
⚽ Monitorando rivais: Flamengo, Palmeiras
⏱️  Verificando a cada 60s
```

---

## Comandos disponíveis no Discord

| Comando | O que faz |
|---------|-----------|
| `!status` | Mostra jogos ao vivo dos rivais agora |
| `!rivais` | Lista os times que estão sendo monitorados |

---

## Lógica de alertas

```
Rival estava GANHANDO → passa a PERDER ou EMPATAR
    → 🚨 "Possível resenha no [Liga]!"

Rival estava PERDENDO/EMPATANDO → passa a GANHAR
    → ✅ "Resenha cancelada"
```

O bot guarda o estado de cada jogo em memória. Se o bot reiniciar durante um jogo, ele começa a monitorar do zero (sem histórico de alertas anteriores).

---

## Limite da API gratuita

O plano free tem **100 requisições/dia**. Com verificação a cada 60s rodando 24h = ~1440 req/dia — estoura o limite.

**Soluções:**

- Rode o bot **só nos horários de jogo** (ex: das 15h às 23h) → ~480 req
- Aumente o intervalo para 120s em `CHECK_INTERVAL = 120` → ~720 req/dia
- Faça upgrade para o plano básico (~$9/mês) para rodar 24h sem preocupação

---

## Estrutura do projeto

```
resenha-bot-py/
├── bot.py            # Código principal
├── requirements.txt  # Dependências Python
├── .env.example      # Modelo de configuração
└── README.md         # Este arquivo
```
