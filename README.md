# telegrammotionbot

Telegram Bot interface for MotionEye on Raspberry Pi

## Requirements



- Telegram bot access token, and user account ID number

- Raspberry Pi OS (raspbian)

- Python 3

- MotionEye instance setup and running natively

- rclone configured with (recommended google drive) account setup as label 'gdrive'

## Features

Control your camera without the need for port forwarding

Telegram command interface for functions such as:
`/photo` `/report` `/motionon` `/notifications`

## Setup

`git clone --depth=1 https://github.com/sealedjoy/telegrammotionbot ~/scripts`
