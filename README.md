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
1. An [ElevenLabs](https://beta.elevenlabs.io/) account  
1. Python download: https://www.python.org/downloads/  

## Setup
### Discord
You will need to set up an Application on the [Discord Developer Portal](https://discord.com/developers/). I won't explain that here.  

### Files
Run `install.bat`.  
This will install the Python packages needed for the bot to run, and will initialise a `secrets.py` file for you to use.

### Keys and Tokens
In that `secrets.py`, you will store two tokens:
1. Your Discord application token
1. Your API key for ElevenLabs (obtained on your Profile).  

### Other Details
The `secrets.py` file also stores `test_guilds` and `owners`, each in arrays.  
This is to try and get Slash Commands working, and to define who can generate video or have an uncapped audio generation limit.  

## Running
Once everything is installed and set up properly, double-clicking `main.py` should work.  
If it brings up a "no program to run this" message, you can Browse for Python from there and then say "always use this program".

## Notes
While the AI is pretty good, sometimes it can mispronounce things.  
Purposely using different words may become necessary to get the result you expect.  
I'll add to the following table with words I come across that you may want to try.
| Original | Replacement |
| :-- | :-- |
| colonel | kernel|
