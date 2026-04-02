# ⚽ ResenhoBot — Python

### Install and Run

```bash
# 1. Enter the project folder
cd resenhoBot

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate         # Linux/Mac
venv\Scripts\activate            # Windows

# Standard execution without virtual environment
python bot.py

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials
````

-----

## Step-by-Step Configuration

### 1\. Create the Discord Bot

1.  Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2.  Click **New Application** → give it a name (e.g., `Resenha Alert`)
3.  Go to **Bot** → click **Add Bot**
4.  Under **Privileged Gateway Intents**, enable:
      - `Server Members Intent`
      - `Message Content Intent`
5.  Click **Reset Token** and copy it → this is your `DISCORD_TOKEN`
6.  Go to **OAuth2 → URL Generator**:
      - Scopes: `bot`
      - Permissions: `Send Messages`, `Embed Links`, `Mention Everyone`
7.  Access the generated URL in your browser to add the bot to your server

### 2\. Configure Rival Teams

Open `bot.py` and edit the `RIVAL_TEAMS` list:

```python
RIVAL_TEAMS = [
    "Vasco",
    "Palmeiras",
    "São Paulo",
    # Add the teams you dislike here
]
```

## Running the Bot

```bash
python bot.py
```

You should see the following in the terminal:

```
✅ Bot online: ResenhoBot#1234
⚽ Monitoring rivals: Flamengo, Palmeiras
⏱️ Checking every 60s
```

-----

## Alert Logic

```
Rival was WINNING → switches to LOSING or DRAWING
    → 🚨 "Possible banter in [League]!"

Rival was LOSING/DRAWING → switches to WINNING
    → ✅ "Banter canceled"
```

The bot keeps the state of each match in memory. If the bot restarts during a game, it starts monitoring from scratch (without previous alert history).

-----

## 🛠️ Project Structure

  * `bot.py`: Bot entry point, contains commands and Discord logic.
  * `tasks/task_update_data.py`: Manages writing to the local JSON file.
  * `tasks/obter_jogos_brasileirao.py`: Selenium script that performs scraping on the GE website.
  * `data/dados_jogos.json`: Stores the current state of the round's matches.

## 🚀 Features

  * **Real-Time Scraping:** Extracts match data (score, teams, and status) directly from GE.
  * **Automatic Update:** Features a background task that updates the database every 2 minutes.
  * **Match Command:** The `!jogos` command displays the full round list with visual indicators:
      * 🟢 **Live**
      * ⬛ **Finished**
      * 🔵 **Upcoming matches**
  * **Rival Filter:** Internal configuration to monitor specific teams the user wants to "keep a close eye on."

-----

## Project Contributors

<table style="width:100%">
    <tr>
        <td align="center">
        <a href="https://github.com/Gl1tch42">
            <img src="https://github.com/Gl1tch42.png" width="100px;" alt="Jean Michel"><br>
            <sub><b>Jean Michel</b></sub>
        </a><br>
        🚀 Lead Developer
        </td>
    </tr>
</table>

-----

### 💡 How to Contribute

Feel free to suggest improvements or report bugs\! To contribute:

1.  **Fork** the project.
2.  Create a **Branch** for your modification (`git checkout -b feature/new-feature`).
3.  **Commit** your changes (`git commit -m 'Adding new alert function'`).
4.  **Push** your branch (`git push origin feature/new-feature`).
5.  Open a **Pull Request**.

> **Note:** If you are developing this bot together for your personal server, feel free to customize the contribution roles based on each person's participation\!

```
```