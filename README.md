# Welcome to the part of the ML training 

### DISCLAIMER
- Prefferably use `python 3.13` since the project was made with this
- Prefferably you're sitting on ubuntu 24.04
```bash
cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.4 LTS"

uname -a

Linux stefan-Latitude-7480 6.8.0-106-generic #106-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 07:58:08 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux

```
## 1.CREATE VENV

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

## 2.REQUIREMENTS - INSTALLING

```bash
python -m pip install -r requirements.txt
```

## 3. INSTALLING MONGODB ON LOCALHOST ([Taken from mongodb documentation for UBUNTU 24.04](https://www.mongodb.com/docs/manual/administration/install-community/?linux-distribution=ubuntu&linux-package=default&operating-system=linux&search-linux=with-search-linux))

### Run this
```bash
sudo apt-get install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
```
### Create the list file `/etc/apt/sources.list.d/mongodb-org-8.2.list` for your version of Ubuntu.

```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.2.list
sudo apt-get update
```

### Run this to install mongodb-community edition

```bash
sudo apt-get install -y mongodb-org
```

### Start mongo service

```bash
sudo systemctl start mongod
```

### If you receive an error similar to the following when starting mongod:

`Failed to start mongod.service: Unit mongod.service not found.`

### Run this

```bash
sudo systemctl daemon-reload
```
### Verify that MongoDB has started successfully.

```bash
sudo systemctl status mongod
● mongod.service - MongoDB Database Server
     Loaded: loaded (/usr/lib/systemd/system/mongod.service; disabled; preset: >
     Active: active (running) since Thu 2026-03-19 10:21:36 EET; 1min 36s ago

/* rest of the output ommited */

```


























