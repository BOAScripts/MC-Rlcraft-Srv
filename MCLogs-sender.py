import subprocess
import requests
import asyncio
from datetime import datetime, timedelta

# Your Discord webhook URL
WEBHOOK_URL = '--MYWEBHOOKURL--'

def get_json(title,desc,color):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    colors = {"blue":2431972,"green":4164619,"red":16711680}
    json ={
    "embeds": [
        {
        "title": title,
        "description": desc,
        "color": colors[color],
        "footer": {
            "text": now
        },
        "fields": []
        }
    ],
    "content": ""
    }
    return json

async def check_logs():
    while True:
        try:
            # Calculate the timestamp for 15 seconds ago
            since_time = (datetime.now() - timedelta(seconds=15)).strftime('%Y-%m-%d %H:%M:%S')
            # Run the journalctl command and capture the output incrementally
            journal_process = subprocess.Popen(["journalctl", "-u", "minecraft-server.service", f"--since={since_time}", "--follow", "--quiet"], stdout=subprocess.PIPE, text=True)
            # Process the log lines as they come in
            for log_line in journal_process.stdout:
                # if user IN
                if "joined the game" in log_line:
                    playerName = log_line.split('joined the game')[0].split(' ')[-2]
                    json = get_json('Player logged in:',playerName,'blue')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                #if user OUT
                elif "left the game" in log_line:
                    playerName = log_line.split('left the game')[0].split(' ')[-2]
                    json = get_json('Player logged out:',playerName,'blue')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                #if server STARTING
                elif "[FML]: Forge Mod Loader version" in log_line:
                    json = get_json('Minecraft server starting:','Please wait for the server UP status before trying to login','green')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                # if server UP
                elif '! For help, type "help" or "?"' in log_line:
                    json = get_json('Minecraft server UP','Ready to slay in RLCraft with the provided IP:PORT','green')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                # if server STOPPING
                elif "[minecraft/MinecraftServer]: Stopping server" in log_line:
                    json = get_json('Minecraft server stopping','Sorry ... wait for maintenance','red')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
            await asyncio.sleep(15)
        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(15)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_logs())