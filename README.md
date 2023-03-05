# Lambda
ElevenLabs? Lambda-11?  
I'm funny.

## About
Originally a Discord bot for generating audio clips using [ElevenLabs' API](https://api.elevenlabs.io/docs#/), Lambda has since expanded to include [OpenAI's API](https://platform.openai.com/docs) for generating conversational text and images.

## Features
### Main application
#### Audio
- Generate audio using [ElevenLabs' API](https://api.elevenlabs.io/docs#/)
  - By default only shows Cloned/Custom voices
  - Updates voice list upon running the generation
- Generate still-frame video using generated audio and provided image URL
  - Start your message with a ! to generate a video instead of audio
  - Dagoth Ur image included because that's likely something you'd want and/or need
- Save all generations (images, audio, and video) locally, in case you wanna refer to them again or something
#### OpenAI
- Generate conversational text using [OpenAI's API](https://platform.openai.com/docs/guides/chat)*
- Generate image using [OpenAI's API](https://platform.openai.com/docs/api-reference/images/create)*  
    - Preface your message with "give me an image of" followed by your prompt to generate an image  

**Limited to "Owners"*  
**Ping the bot to get a response*
    
  
### Side features
- Script for generating sample clips for creating Clone voices
- [Custom wrapper](https://github.com/Jordy3D/LambdaBot/blob/main/BaneElevenLabs.py) for ElevenLabs' API included because ease of use is fun!
- [Custom wrapper](https://github.com/Jordy3D/LambdaBot/blob/dev/BaneOpenAI.py) for OpenAI's API, relying on [OpenAI's Python library](https://github.com/openai/openai-python) to streamline the use in the bot

## Requirements
1. An [ElevenLabs](https://beta.elevenlabs.io/) account  
1. A paid [OpenAI](https://platform.openai.com/) account
1. Python download: https://www.python.org/downloads/  

## Setup
### Discord
You will need to set up an Application on the [Discord Developer Portal](https://discord.com/developers/). I won't explain that here.  

### Files
Run `install.bat`.  
This will install the Python packages needed for the bot to run, and will initialise a `secrets.py` file for you to use.

### Keys and Tokens
In that `secrets.py`, you will store your API tokens:  
| Key | Value | Type |
|--:|:--|:--:|
| `token` | Your Discord application token | `str` |
| `xi` | Your API key for ElevenLabs (obtained on your Profile) | `str` |
| `openaikey` | Your API key for OpenAI (obtained on your Profile) | `str` |


### Other Details
The `secrets.py` file also stores some other relevant information.
| Key | Value | Type |
|--:|:--|:--:|
| `test_guilds` | List of server IDs that the bot will respond to<br>*May be required for the /command to appear in the first place* | `list` |
| `owners` | List of user IDs that can use the OpenAI features<br>Defines who can create video outputs, as well as who can generate results longer than 100 characters | `list` |

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
