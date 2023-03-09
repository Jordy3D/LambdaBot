#  ▄   ▄
# ▄██▄▄██▄          ╔╗ ┌─┐┌┐┌┌─┐█
# ███▀██▀██         ╠╩╗├─┤│││├┤ █
# ▀███████▀         ╚═╝┴ ┴┘└┘└─┘█
#   ▀███████▄▄      ▀▀▀▀▀▀▀▀▀▀▀▀█▀
#    ██████████▄
#  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█▀

import asyncio
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
import BaneOpenAI
import DagothVideo

# TODO:



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

# set sub tier 
paid_user = BaneElevenLabs.get_user_data().tier != "free"

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
    if message.author.bot:
        return

    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        if message.author.id in owners:
            # if message starts with give me an image of, send an image
            if "give me an image of" in message.content:
                prompt = message.content.replace("give me an image of", "")
                # remove the mention
                prompt = prompt.replace(f"<@!{bot.user.id}>", "")

                # give ephemeral message
                temp = await message.channel.send("Generating image...", reference=message, mention_author=None)
                
                image = BaneOpenAI.AIImage()
                image.generate_image(prompt)
                image.save_images()

                await temp.delete()

                # send image as a reply, with the text "Here's your image!"
                await message.reply("Here's your image!", file=disnake.File(image.image_path))
                log(f"Sent image to {message.author.name}!", "OPENAI", message.guild)
            else:
                # set the bot to "typing" while it generates a response
                async with message.channel.typing(): 
                    response = BaneOpenAI.generate_chat(message.content)
                
                await message.reply(response)
                log(f"Sent response to {message.author.name}!", "OPENAI", message.guild)
        else:
            # not implemented yet
            temp = await message.reply("You don't have the permissions to use this feature!", mention_author=False)
            log(f"{message.author.name} tried to use a feature they don't have access to!", "SYSTEM", message.guild)
            await asyncio.sleep(5)
            await temp.delete()


# endregion

# region Slash Commands

# region AI Voice Generator
dagoth_voices = BaneElevenLabs.get_voices(cloned=paid_user)

generating = False

# slash command to accept a message and send it to an API
@bot.slash_command(name="dagoth",
                     description="Responds with AI generated audio.",
                        pass_context=True,
                        auto_sync=True)
@commands.cooldown(1, 5, commands.BucketType.user)
# add a field that only accepts the keys in the dagoth_voices dict
async def dagoth(interaction: disnake.CommandInteraction, message: str, voice: str = commands.Param(choices=dagoth_voices.keys()), stability: float = 0.75, similarity_boost: float = 0.75, image: str = None):
    # refresh the dagoth_voices dict
    dagoth_voices = BaneElevenLabs.get_voices(cloned=paid_user)

    # get generating bool from global
    global generating

    if generating == True:
        await interaction.response.send_message("Currently busy, please try again later.", ephemeral=True)
        return

    # if message is too long, return
    if len(message) > 100:
        if len(message) > 2000:
            await interaction.response.send_message("Message is too long!", ephemeral=True)
            return
        # owners can bypass this
        if interaction.author.id not in owners:
            await interaction.response.send_message("Message is too long!", ephemeral=True)
            return

    video = False
    # if the message author is an owner, and the message starts with !, set video to true
    if interaction.author.id in owners and message.startswith("!"):
        video = True
        message = message[1:]
    elif interaction.author.id not in owners and message.startswith("!"):
        await interaction.response.send_message("Only special people can use this!", ephemeral=True)
        return
      
    generating = True
    await interaction.response.defer(with_message="Generating...")

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

    generating = False

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