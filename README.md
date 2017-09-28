# Mousey

[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/FrostLuma/Mousey/blob/master/LICENSE)
[![discord](https://discordapp.com/api/guilds/288369367769677826/widget.png)](http://discord.gg/Bd7BuGh)

Discord Bot written by FrostLuma to provide powerful moderation and utility features.

# Using Mousey

Mousey can be invited to any discord guild using [this invite link](https://discordapp.com/oauth2/authorize?client_id=288369203046645761&scope=bot&permissions=500559095),
for support join [our support guild](http://discord.gg/u8dHda6).
I try to keep Mousey running 24/7,
any downtime will be announced in advance in the support guild.

Read the [documentation (TODO)](https://frostluma.github.io/Mousey/)
to find out how to utilise all of Mouseys features!

To run your own instance simply install the requirements,
copy and rename `config_example.py` to `config.py`
and fill it our with your credentials.

# Requirements

- Python 3.6
  - aiodns
  - aiohttp
  - aioredis
  - asyncpg
  - cchardet
  - discord.py (1.0 or above), voice branch
  - emoji
  - markovify
  - psutil
  - uvloop
- Redis
- PostgreSQL

To install the required python modules simply run `pip install -r requirements.txt`.
