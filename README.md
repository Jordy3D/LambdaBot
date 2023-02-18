# Lambda
ElevenLabs? Lambda-11?  
I'm funny.

## Features
### Main application
- Generate audio using [ElevenLabs' API](https://api.elevenlabs.io/docs#/)
  - By default only shows Cloned/Custom voices
  - Updates voice list upon running the generation
- Generate still-frame video using generated audio and provided image URL
  - Dagoth Ur image included because that's likely something you'd want and/or need
- Save all generations (images, audio, and video) locally, in case you wanna refer to them again or something
  
### Side features
- Script for generating sample clips for creating Clone voices
- [Custom wrapper](https://github.com/Jordy3D/LambdaBot/blob/main/BaneElevenLabs.py) for ElevenLabs' API included because ease of use is fun!

## Requirements
Python download: https://www.python.org/downloads/  
With Python installed, you need to install [Disnake](https://docs.disnake.dev/en/stable/).  
This can be done by running the following command in CMD/Powershell:  
`pip install disnake`

## Setup
### Discord
You will need to set up an Application on the [Discord Developer Portal](https://discord.com/developers/docs/intro). I won't explain that here.  

### Keys and Tokens
You also need to create a `secrets.py` file next to `main.py`.  
In that file, you will store your Discord application token, and the API key for ElevenLabs (obtained on your Profile).  
Your file at the end should look something like the following:
```py
token = 'YOUR DISCORD TOKEN THING HERE'
xi = 'YOUR ELEVENLABS TOKEN HERE'
```

## Running
Once everything is installed and set up properly, double-clicking `main.py` should work.  
If it brings up a "no program to run this" message, you can Browse for Python from there and then say "always use this program".
