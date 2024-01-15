# About

I wanted to host a minecraft server to play with my lil bro. I tend to over-complicated stuff. Here below my RlCraft 2.9.3 installation.

This repo contains the install instructions as well as the custom files that I created to manage my Minecraft server.

I use systemctl units to start the minecraft server when booting and send specific logs to a discord webhook.

# Server info

VMWare - headless Ubuntu server 22.04:
 - 4 CPU threads
 - 10GB RAM
 - 80GB Storage
 - Bridged connection

 ## Users

|user|type|
| - | - |
|master|sudoer|
|mcuser|low priv. user to launch the minecraft server|
||mcrcon service|

-> Check Bitwarden for passwords (Minecraft - Rlcraft)

## Software installed

```bash
sudo apt-get install openjdk-8-jre
sudo apt-get install nano
sudo apt-get install python3.11
sudo apt-get install git
sudo apt-get install make
sudo apt-get install cron
# mcrcon
git clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
make
sudo make install
```

# Minecraft Config

## Install

I wanted to play with the modpack RLCraft 2.9.3. So I had to use the `.jar` from [Forge](https://files.minecraftforge.net/net/minecraftforge/forge/index_1.12.2.html).

1. Initialize the forge minecraft server:
```bash
# as mcuser 
mkdir ~/mc-server
cd mc-server
wget 'URL to .jar'
java -jar JARNAME.jar --nogui
# Accept Eula
nano eula.txt # set true
```

2. Download & copy the modpack in ~/mc-server

- Download the Server pack zip file from curseforge and unzip it.
- Use `scp` or `wget -r` with `python -m http.server` to copy it in `~/mc-server`


## Import World (Optional)

- Download the `/World` folder
- Upload content into `~/mc-server/World` 

## Setup start and stop scripts

I use 2 scripts with a systemctl unit to start and stop the minecraft server. Those are located in `/home/mcuser`

- [start](./start.sh)
- [stop](./stop.sh)

## Setup python script to send some logs to discord

I use 1 script to monitor the server logs and send some of them to a discord channel. Also located in `/home/mcuser`

- [MCLogs-Sender](./MCLogs-sender.py)

## Setup custom configs

Review `~/mc-server/server.properties` and `~/mc-server/ops.json` and modify accordingly.

- mcrcon needs `enable-rcon=true` in the server.properties
- set yourself as an op in `ops.json`

# Systemctl units

## minecraft-server.service

Service that manage the start and stop of the minecraft server. It will start the minecraft server on system boot.

```bash
# as master
cd /lib/systemd/system
sudo nano minecraft-server.service
```

```ini
[Unit]
Description=Minecraft Server
After=network.target minecraft-monitor.service
Wants=minecraft-monitor.service

[Service]
WorkingDirectory=/home/mcuser/mc-server
User=mcuser
Group=mcuser
Restart=on-failure
RestartSec=20 5
ExecStart=/home/mcuser/start.sh
ExecStop=/home/mcuser/stop.sh

[Install]
WantedBy=multi-user.target
```

## minecraft-monitor.service

Service that manages the function to send logs to my Discord channel via a webhook

```bash
cd /lib/systemd/system
sudo nano minecraft-monitor.service
```

```ini
[Unit]
Description=Minecraft Server Monitor
After=network.target

[Service]
WorkingDirectory=/home/mcuser
User=mcuser
Group=mcuser
Restart=on-failure
RestartSec=20 5
ExecStart=/usr/bin/python3 /home/mcuser/MCLogs-sender.py

[Install]
WantedBy=multi-user.target
```

## Start the services

```bash
sudo systemctl enable minecraft-monitor.service
sudo systemctl enable minecraft-server.service
```

Then reboot to fix problems :)

# Port forwarding

/!\ DO NOT SHARE YOUR PUBLIC IP TO UNTRUSTED USERS /!\ 

To be able to access my server from the outside network I need to give my `publicIP:PORT` to players that want to join.

The port has to be the same as in the `server.properties`. Default is `25565`.

Having the port and hostname/localip necessary for my minecraft server, I had to open the port on my modem. RTFM of the modem model.

# Maintenance

## World backup

`mcuser@mc001:~$`

### Backup script

```bash
mkdir world-backups
nano backup.py
```

- [backup.py](./backup.py)

### CRON

Setup a cron job to execute the backup script every day at 7AM.

```bash
crontab -e
0 7 * * * /usr/bin/python3 /home/mcuser/backup.py
```

## Auto-reboot

`master@mc001:~$`

### CRON

Setup a cron job to reboot the server every day at 7:15AM

```bash
sudo su
crontab -e
10 7 * * * /usr/local/bin/mcrcon -H localhost -p {your-mcrcon-psw-here} "say Server REBOOT in 5 minutes !!!" && /usr/sbin/shutdown -r +5
# saving to /tmp is normal. cron checks for syntax errors before putting it in the correct location
```
