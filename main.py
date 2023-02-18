#  ▄   ▄
# ▄██▄▄██▄          ╔╗ ┌─┐┌┐┌┌─┐█
# ███▀██▀██         ╠╩╗├─┤│││├┤ █
# ▀███████▀         ╚═╝┴ ┴┘└┘└─┘█
#   ▀███████▄▄      ▀▀▀▀▀▀▀▀▀▀▀▀█▀
#    ██████████▄
#  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█▀

import os
import os.path
import re
import time
from datetime import date
import json
import disnake
import requests
from disnake import app_commands, SlashCommand
from disnake.ext import commands, tasks
from disnake.ext.commands import has_permissions, MissingPermissions, cooldown
# Permissions: https://discordpy.readthedocs.io/en/latest/api.html#discord.Permissions
from disnake.utils import get

import secrets # secrets.py stores the API key

import BaneElevenLabs
import DagothVideo

# TODO:
# Auto prune role >>>>> This will be left to Dyno

# Add Test Guilds to Settings.JSON
# Pretty up Module embed <<<<<
# Automate Module embed


# region General Functions
def get_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def start():
    if not os.path.exists("logs"):
        os.mkdir("logs")

    with open(f"logs/[{date.today()}] log.txt", "a") as txt:
        txt.write(f"\n===== NEW LOG START =====\n")

    log("Starting Bot...", "SYSTEM")

def log(message, type, guild=None):
    if type == "SYSTEM" or type == "UPDATE" or guild == None:
        path = f"logs/[{date.today()}] log.txt"
    else:
        if not os.path.exists(f"logs/{guild.id}"):
            os.mkdir(f"logs/{guild.id}")

        path = f"logs/{guild.id}/[{date.today()}] log.txt"

    log_msg = f"[{get_time()}] {'[' + type + ']':10s} {message}"
    print(log_msg)
    with open(path, "a", encoding='utf-8') as txt:
        txt.write(f"{log_msg}\n")

def error(e, guild=None):

    if guild == None:
        path = f"logs/{guild.id}/[{date.today()}] log.txt"
        log(f"{e}", "ERROR")
    else:
        path = f"logs/{guild.id}/[{date.today()}] log.txt"
        log_msg = f"[{get_time()}] {'[ERROR]':10s} {e}"
        print(log_msg)
        with open(path, "a", encoding='utf-8') as txt:
            txt.write(f"{log_msg}\n")

def simple_embed(title="", description="", thumbnail="", color=0xFFFFFF, footer=""):
    embed = disnake.Embed(title=title, description=description, color=color)
    embed.set_author(name="", icon_url="")
    embed.set_thumbnail(url=thumbnail)
    # embed.add_field(name="", value="", inline=False)
    # embed.add_field(name="", value="", inline=False)
    embed.set_footer(text=footer)
    return embed

# endregion

# region ===== Main =====

# if owners is not set in secrets.py, set it to an empty list
owners = secrets.owners if hasattr(secrets, "owners") else []
# if test_guilds is not set in secrets.py, set it to an empty list
test_guilds = secrets.test_guilds if hasattr(secrets, "test_guilds") else []

# check if secrets.py exists
if not os.path.exists("secrets.py"):
    log("secrets.py not found!", "ERROR")
    exit()
# check if secrets.token exists and secrets.xi exists
if not hasattr(secrets, "token"):
    log("secrets.token not found!", "ERROR")
    exit()
if not hasattr(secrets, "xi"):
    log("secrets.xi not found!", "ERROR")
    exit()

start()

# endregion

# create bot and make it sync commands globally
bot = commands.Bot(command_prefix=disnake.ext.commands.when_mentioned, owner_ids = set(owners), sync_commands=True, test_guilds=test_guilds)

# region ===== Commands and Events =====

# region Events
@bot.event
async def on_ready():
    log(f"{bot.user.name} is online for {len(bot.users)}!", "SYSTEM")
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching,
                                                        name=f"over {len(bot.users)} users."))

@bot.event
async def on_guild_join(guild):
    log(f"Joined {guild.name}!", "SYSTEM")
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching,
                                                        name=f"over {len(bot.users)} users."))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

# endregion

# region Slash Commands

# region AI Voice Generator
dagoth_voices = BaneElevenLabs.get_voices(cloned=True)
# slash command to accept a message and send it to an API
@bot.slash_command(name="dagoth",
                     description="Responds AI generated audio.",
                        pass_context=True,
                        auto_sync=True)
@commands.cooldown(1, 5, commands.BucketType.user)
# add a field that only accepts the keys in the dagoth_voices dict
async def dagoth(interaction: disnake.CommandInteraction, message: str, voice: str = commands.Param(choices=dagoth_voices.keys()), stability: float = 0.75, similarity_boost: float = 0.75, image: str = None):
    # refresh the dagoth_voices dict
    dagoth_voices = BaneElevenLabs.get_voices(cloned=True)

    # if message is too long, return
    if len(message) > 100:
        # owners can bypass this
        if interaction.author.id not in owners:
            await interaction.response.send_message("Message is too long!", ephemeral=True)
            print(f"Message is too long! ({len(message)}/100)\n {message}")
            return

    video = False
    # if the message author is an owner, and the message starts with !, set video to true
    if interaction.author.id in owners and message.startswith("!"):
        video = True
        message = message[1:]
    elif interaction.author.id not in owners and message.startswith("!"):
        await interaction.response.send_message("Only special people can use this!", ephemeral=True)
        return
    
    await interaction.response.defer(with_message="Generating audio...")

    # if message doesn't end with a period, question mark, or exclamation point, add a period
    if message[-1] not in [".", "?", "!"]:
        message += "."

    # get the current unix time
    generation_time = time.time()
    # set the name of the audio file to "time - voice - author username.mp3"
    file_name = f"{generation_time} - {voice} - {interaction.author.name}"

    # if the audio, video, and image folders don't exist, create them
    if not os.path.exists("audio"):
        os.mkdir("audio")
    if not os.path.exists("video"):
        os.mkdir("video")
    if not os.path.exists("image"):
        os.mkdir("image")

    if video:
        # if an image URL is provided, save it to image/file_name.png
        if image != None:
            image_path = f"image/{file_name}.png"
            image_content = requests.get(image).content
            
            if not DagothVideo.save_and_crop_image(image_content, image_path):
                await interaction.edit_original_message(content="Image failed to download!")
                return
        else:
            image_path = "dagoth.png"
    
    if BaneElevenLabs.generate_audio(dagoth_voices[voice], message, stability, similarity_boost, file_name=f"audio/{file_name}.mp3"):
        # if video is true, send the video file
        if video:
            DagothVideo.dagoth_video(audio_path=f"audio/{file_name}.mp3", output_file=f"video/{file_name}.mp4", image_path=image_path)
            
            await interaction.edit_original_message(content="Here you go!", file=disnake.File(f"video/{file_name}.mp4"))
            log(f"Generated video for {interaction.author.name}!", "DAGOTH")
        else:
            # send the audio file
            await interaction.edit_original_message(content="Here you go!", file=disnake.File(f"audio/{file_name}.mp3"))
            log(f"Generated audio for {interaction.author.name}!", "DAGOTH")
    else:
        await interaction.edit_original_message(content="Something went wrong!")
        log(f"Something went wrong for {interaction.author.name}!", "DAGOTH")

# endregion

# endregion

# endregion

# region Loops

@tasks.loop(seconds=60)
async def update_presence():
    log("Updating presence...", "UPDATE")
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching,
                                                        name=f"over {len(bot.users)} users."))

# endregion

bot.run(secrets.token)