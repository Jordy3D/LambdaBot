#  ▄   ▄
# ▄██▄▄██▄          ╔╗ ┌─┐┌┐┌┌─┐█
# ███▀██▀██         ╠╩╗├─┤│││├┤ █
# ▀███████▀         ╚═╝┴ ┴┘└┘└─┘█
#   ▀███████▄▄      ▀▀▀▀▀▀▀▀▀▀▀▀█▀
#    ██████████▄
#  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█▀

import asyncio
import datetime
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

import BaneHelper
import BaneElevenLabs
import BaneOpenAI
import DagothVideo
import BaneRemind

# TODO:



# region General Functions

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

    log_msg = f"[{BaneHelper.get_time()}] {'[' + type + ']':10s} {message}"
    print(log_msg)
    with open(path, "a", encoding='utf-8') as txt:
        txt.write(f"{log_msg}\n")

def error(e, guild=None):

    if guild == None:
        path = f"logs/{guild.id}/[{date.today()}] log.txt"
        log(f"{e}", "ERROR")
    else:
        path = f"logs/{guild.id}/[{date.today()}] log.txt"
        log_msg = f"[{BaneHelper.get_time()}] {'[ERROR]':10s} {e}"
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

async def delete_after(seconds, message):
    await asyncio.sleep(seconds)
    await message.delete()

# endregion



# region Settings


class LambdaSettings:
    def __init__(self):
        self.XI_use_only_cloned_voices = True
        self.XI_allow_all_audio = False
        self.XI_allow_all_video = False
        self.OAI_allow_all_chat = False
        self.OAI_allow_all_dalle = False
        self.XI_allowed_roles_audio = []
        self.XI_allowed_roles_video = []
        self.OAI_allowed_roles_chat = []
        self.OAI_allowed_roles_dalle = []
        self.OAI_image_size = "medium"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_lambda_settings(settings: LambdaSettings, guild: str):
    if guild == None:
        path = f"lambda_settings/settings.json"
    else:
        path = f"lambda_settings/{guild}/settings.json"

    with open(path, "w") as f:
        json.dump(settings.__dict__, f, indent=4)

def load_lambda_settings(guild=None):
    if guild == None:
        path = f"lambda_settings/settings.json"
    else:
        path = f"lambda_settings/{guild}/settings.json"

    ls = LambdaSettings()
    
    if not os.path.exists(path):
        log("No settings found, using default settings", "SYSTEM", guild if guild != None else None)
        save_lambda_settings(ls, guild if guild != None else None)
    else:
        data = load_json(path)
        ls.__dict__.update(data)

    return ls
# endregion

# region ===== Main =====

# set sub tier for ElevenLabs 
paid_user = BaneElevenLabs.get_user_data().tier != "free"

# if owners is not set in secrets.py, set it to an empty list
owners = secrets.owners if hasattr(secrets, "owners") else []
# if test_guilds is not set in secrets.py, set it to an empty list
test_guilds = secrets.test_guilds if hasattr(secrets, "test_guilds") else []

settings = load_lambda_settings()

member_count = 0

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

@bot.command(name="remindme", aliases=["remind", "remind_me", "remind-me"])
async def remindme(ctx, time, *, message):

    time_format = "D" # can be D, t, or F

    if time.endswith("s"):
        seconds = int(time[:-1])
        time_format = "t"
    elif time.endswith("m"):
        seconds = int(time[:-1]) * 60
        time_format = "t"
    elif time.endswith("h"):
        seconds = int(time[:-1]) * 60 * 60
        time_format = "t"
    elif time.endswith("d"):
        seconds = int(time[:-1]) * 60 * 60 * 24
        time_format = "F"
    else:
        await ctx.send("Invalid time format, please use s, m, h, or d.")
        return
    


    time_to_remind = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    time_to_remind = time_to_remind.timestamp()
    BaneRemind.add_reminder(message, time_to_remind, ctx.author.id)

    reminder_message = f"Ok, I'll remind you in {time}, at <t:{int(time_to_remind)}:{time_format}>."

    await ctx.send(reminder_message)

@tasks.loop(seconds=5)
async def check_reminders():
    reminders = BaneRemind.get_reminders()
    if reminders == None or len(reminders) == 0:
        return

    for reminder in reminders:
        if reminder["time"] < datetime.datetime.now().timestamp():
            # dm user
            user = await bot.fetch_user(reminder["user"])
            await user.send(f"Reminder: {reminder['text']}")
            # remove reminder
            BaneRemind.remove_reminder(reminder)


async def update_presence():
    await bot.change_presence(activity=disnake.Activity(
                                type=disnake.ActivityType.watching,
                                name=f"over {BaneHelper.get_total_members(bot)} users."))

# region Events
@bot.event
async def on_ready():
    log(f"{bot.user.name} is online for {BaneHelper.get_total_members(bot)}!", "SYSTEM")
    await update_presence()
    
    # start any loops
    update_presence_loop.start()
    check_reminders.start()

@bot.event
async def on_guild_join(guild):
    log(f"Joined {guild.name}!", "SYSTEM")
    await update_presence()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author == bot.user:
        return
    
    if message.channel.type == disnake.ChannelType.private:
        if message.author.id not in owners:
            return
    
    if bot.user.mentioned_in(message):
        # if the first word after the mention is a command, run it
        if message.content.split(" ")[1] in command_list:
            await bot.process_commands(message)
        else:
            try:
                await openai(message)
            except Exception as e:
                await message.reply(f"Error: {e}")


async def cant_use_feature(message):
    temp = await message.reply("You don't have the permissions to use this feature!", mention_author=False)
    log(f"{message.author.name} tried to use a feature they don't have access to!", "SYSTEM", message.guild)

    await delete_after(5, temp)



async def openai(message):
    try:
        # if message starts with give me an image of, send an image
        if "give me an image of" in message.content:
            can_use = False
            if message.author.id in owners:
                can_use = True
            else:
                if settings.OAI_allow_all_dalle or BaneHelper.has_role(message.author, settings.OAI_allowed_roles_dalle):
                    can_use = True

            if not can_use:
                await cant_use_feature(message)
                return

            prompt = message.content.replace("give me an image of", "")
            prompt = prompt.replace(f"<@!{bot.user.id}>", "")

            temp = await message.channel.send("Generating image...", reference=message, mention_author=None)
            
            image = BaneOpenAI.AIImage()
            try:
                image.generate_image(prompt, size=settings.OAI_image_size)
            except:
                await temp.edit(content="Something went wrong!")
                error(f"Something went wrong while generating an image for {message.author.name}! Prompt: {prompt}", message.guild)
                return
                
            image.save_images()

            await temp.delete()

            await message.reply("Here's your image!", file=disnake.File(image.image_path))
            log(f"Sent image to {message.author.name}!", "OPENAI", message.guild)
        else:
            can_use = False
            if message.author.id in owners:
                can_use = True
            else:
                if settings.OAI_allow_all_chat or BaneHelper.has_role(message.author, settings.OAI_allowed_roles_chat):
                    can_use = True            

            if not can_use:
                await cant_use_feature(message)
                return
            
            async with message.channel.typing(): 
                try:
                    response = BaneOpenAI.generate_chat(message.content)
                except:
                    response = "Something went wrong!"
            
            await message.reply(response)
            
            if response == "Something went wrong!":
                error(f"Something went wrong while generating a response for {message.author.name}! Prompt: {message.content}", message.guild)
            else:
                log(f"Sent response to {message.author.name}!", "OPENAI", message.guild)
                
    except Exception as e:
        error(e, message.guild)
        temp = await message.reply("Something went wrong!", mention_author=False)
        
        await delete_after(5, temp)

# endregion

# region Slash Commands

# region AI Voice Generator

dagoth_voices = BaneElevenLabs.get_voices(cloned=settings.XI_use_only_cloned_voices)
generating = False

@bot.slash_command(name="dagoth",
                   description="Responds with AI generated audio.",
                   pass_context=True,
                   auto_sync=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def dagoth(interaction: disnake.CommandInteraction, message: str, voice: str = commands.Param(choices=dagoth_voices.keys()), stability: float = 0.75, similarity_boost: float = 0.75, image: str = None):
    # refresh the dagoth_voices dict
    dagoth_voices = BaneElevenLabs.get_voices(cloned=settings.XI_use_only_cloned_voices)

    video = False
    if message.startswith("!"):
        video = True
        message = message[1:]

    can_use = False
    if interaction.author.id in owners:
        can_use = True
    elif video:        
        if settings.XI_allow_all_video or BaneHelper.has_role(interaction.author, settings.XI_allowed_roles_video):
            can_use = True
    else:
        if settings.XI_allow_all_audio or BaneHelper.has_role(interaction.author, settings.XI_allowed_roles_audio):
            can_use = True
    
    if not can_use:
        await cant_use_feature(message)
        return

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
     
    generating = True
    await interaction.response.defer(with_message="Generating...")

    # if message doesn't end with a period, question mark, or exclamation point, add a period
    if message[-1] not in [".", "?", "!"]:
        message += "."

    generation_time = time.time()
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

@tasks.loop(seconds=300)
async def update_presence_loop():
    global member_count

    member_check = BaneHelper.get_total_members(bot)

    if member_count != member_check:
        member_count = member_check

        log("Updating presence...", "UPDATE")
        await update_presence()

# endregion





# set command_list to the names of all commands and their aliases
command_list = []
for command in bot.commands:
    command_list.append(command.name)
    for alias in command.aliases:
        command_list.append(alias)

bot.run(secrets.token)