# Minecraft Hypixel Bedwars Stats Overlay

The Minecraft Hypixel Bedwars Stats Overlay is a tool designed to enhance your gameplay by providing real-time statistics for all players in your lobby. This tool fetches player statistics including Level, Final Kill Death Ratio (FKDR), Winstreak, and Win Loss Ratio (WLR), using Minecraft's log files, the Mojang API, and the Hypixel API.

## Features
* Access statistics for each player in your lobby to access your competition.
* Automatically add and remove players as they join your lobby, leave, or get final killed.
* Support for multiple clients: Vanilla/Forge, Badlion, and Lunar Minecraft clients.

## Easy-Run Method for Windows Users
For Windows users, running the provided overlay.exe file eliminates the need to install Python and its libraries. However, you will still require a [Hypixel API key](https://developer.hypixel.net/). Once obtained, you must enter this key into your .env file in the format: `HYPIXEL_API_KEY=YOUR_API_KEY_HERE`


## Prerequisites
*  Python 3.x installed on your system
* Required Python libraries. Install them using the command: `python -m pip install requests Pillow python-dotenv`
* A Hypixel API key: [Get it here!](https://developer.hypixel.net/)

## Installation/Usage
* Download the project files or clone the project repository to your local machine 
* Install required python libraries (and Python if not already installed)
* Paste your Hypixel API key in the .env file: `HYPIXEL_API_KEY=YOUR_API_KEY_HERE`
* run the `overlay.py` using `python overlay.py` or `py overlay.py` inside the fodler containing overlay.py
* Select your Minecraft client (Vanilla/Forge, Badlion, Lunar)
* When in a bedwars lobby, type `/who` in-game to load all users not in overlay


