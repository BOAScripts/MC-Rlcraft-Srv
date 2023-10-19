import subprocess
import requests
import asyncio
from datetime import datetime, timedelta
import json

# Your Discord webhook URL
WEBHOOK_URL = '--MYWEBHOOKURL--'

def get_player_pp(playerName,usercacheloc):
    # Extract json from local file
    try:
        with open(usercacheloc, 'r') as f:
            usercachedata = json.loads(f.read())
        # Find uuid of playerName
        for player in usercachedata:
            if player["name"] == playerName:
                player_uuid = player["uuid"]
        # return url of PP
        player_pp_url = f"https://laby.net/texture/profile/head/{player_uuid}.png?size=64"
        return player_pp_url
    except Exception as e:
        print("Error: ", e)

def get_json(title,desc,color):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    colors = {"blue":255,"darkgreen":32768,"lightgreen":65280,"red":16711680,"lightblue":760214}

    if 'Player' in title:
        pp_url = get_player_pp(desc,'/home/mcuser/mc-server/usercache.json')
    else:
        pp_url = ""

    json ={
    "embeds": [
        {
        "title": title,
        "description": desc,
        "color": colors[color],
        "footer": {
            "text": now
        },
        "fields": [],
        "image":{
            "url":pp_url
        },
        "thumbnail": {
            "url": "https://raw.githubusercontent.com/BOAScripts/MC-Rlcraft-Srv/main/src/server-icon-1.png"
        }
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
                    json = get_json('Player logged in:',playerName,'lightblue')
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
                    json = get_json('Minecraft server starting:','Please wait for the server UP status before trying to login','darkgreen')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                # if server UP
                elif '! For help, type "help" or "?"' in log_line:
                    json = get_json('Minecraft server UP','Ready to slay in RLCraft with the provided IP:PORT','lightgreen')
                    # print(json)
                    requests.post(WEBHOOK_URL, json=json)
                # if server STOPPING
                elif "[Server thread/INFO] [minecraft/MinecraftServer]: Stopping server" in log_line:
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