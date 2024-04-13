import discord
from discord import *
from discord import app_commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
from discord import File
from PIL import Image
import requests
from io import BytesIO
import io
import contextlib
import sys
from time import sleep
import time
from important_stuff import main_guild
import json
import asyncio
load_dotenv()

with open("Test Database/log_channels.json") as f:
    log_channels = json.load(f)

os.getenv
intents = Intents.default()
caliente = Client(intents=intents)
tree = app_commands.CommandTree(caliente)

intents.guilds = True
intents.invites = True

@caliente.event
async def on_ready():
    print(f"Logged on as {caliente.user.name}")
    await tree.sync()
    commands = tree.get_commands()
    print(f"Synced {len(commands)} commands")
    for command in commands:
        print(f"Synced command: {command.name}")
    print(f"Sync commands")

@caliente.event
async def on_guild_remove(guild: discord.Guild):
    print(f"Left guild {guild.name}")
    channel_id = main_guild.guild_channels["Guild left"]
    channel = caliente.get_channel(channel_id)
    if str(guild.id) in log_channels:
        del log_channels[str(guild.id)]
        with open("Test Database/log_channels.json", "w") as f:
            json.dump(log_channels, f)
    if channel is not None:
        await channel.send(f"Left guild {guild.name}")
    else:
        print(f"Couldn't find channel with ID {channel_id}")
@caliente.event
async def on_guild_join(guild: discord.Guild):
    new_guild_data = {
        "guild_name": guild.name,
        "logging_channel": {
            "channel_id": "your-channel-id",  # Replace with your actual channel ID
            "bot_name_in_guild": caliente.user.name
        }
    }
    log_channels[str(guild.id)] = new_guild_data
    with open("Test Database/log_channels.json", "w") as f:
        json.dump(log_channels, f)
    print(f"Joined guild {guild.name}")
    channel_id = main_guild.guild_channels["Guild Joined"]
    channel = guild.get_channel(channel_id)
    if channel is not None:
        await channel.send(f"Joined guild {guild.name}")
    else:
        print(f"Couldn't find channel with ID {channel_id}")
@caliente.event
async def on_message(message: discord.Message, user: discord.User, interaction: discord.Interaction, text: str = "Commit from bot"):
    if user.id != 489061310022156302:
        return
    if message.content == "":
        await interaction.response.send_message("Committing changes...")
        os.system("git add .")
        os.system(f"git commit -m '{text}'")
"""Moderation Commands"""
@tree.command(
        name="setlogchannel",
        description="Sets the logging channel for the bot"
)

@caliente.event
async def setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.guild is None or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("This command can only be used in a server by users with Manage Server permission.", ephemeral=True)
        return
    new_guild_data = {
        "guild_name": interaction.guild.name,
        "logging_channel": {
            "channel_id": channel.id,
            "bot_name_in_guild": caliente.user.name
        }
    }
    log_channels[str(interaction.guild.id)] = new_guild_data
    with open("Test Database/log_channels.json", "w") as f:
        json.dump(log_channels, f)
    await interaction.response.send_message(f"Logging channel set to {channel.mention}")
@tree.command(
    name="ban",
    description="bans the FUCKING PIECES OF SHIT"
)
@caliente.event

async def ban(interaction: discord.Interaction, user: discord.User, resonitea: str="No reason given"):
    if interaction.guild is None or not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("This command can only be used in a server by users with Ban Members permission.", ephemeral=True)
        return

    try:
        # Attempt to ban the user
        await interaction.guild.ban(user, reason=resonitea)
        await interaction.response.send_message(f"User {user} has been banned for reason: {resonitea}")
        print(f"{interaction.message.author} has banned {user} from guild: {interaction.guild}")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban this user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while trying to ban the user: {e}", ephemeral=True)
@tree.command(
        name="kick",
        description="Kicks the dude.........uh"
)
@caliente.event
async def kick(interaction: discord.Interaction, user: discord.User):
    if interaction.guild is None or not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("This command can only be used in a server by users with Kick Members permission.", ephemeral=True)
        return
    try:
        await interaction.guild.kick(user)
        await interaction.response.send_message(f"Kicked {user}")
        #finding Log channel
        logging_id = log_channels[interaction.guild.id]["logging_channel"]["channel_id"]
        logging_channel = interaction.guild.get_channel(logging_id)
        if logging_channel is not None:
            await logging_channel.send(f"Kicked {user}")
        else:
            print(f"Couldn't find channel with ID {logging_id} but kicked user")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to kick this user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while trying to kick the user: {e}", ephemeral=True)
"""Voice Commands"""
@tree.command(
    name="joinvc",
    description="pffff HAHAHAHAA"
)
@caliente.event
async def joinvc(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        voice_channel = interaction.user.voice.channel

        try:
            voice_client = await voice_channel.connect()
            await voice_client.play(discord.FFmpegPCMAudio(''))
            await interaction.response.send_message("Connect to voice channel!")
        except discord.ClientException:
            await interaction.response.send_message("Already connected to a vc.")
    else:
        await interaction.response.send_message("You need to be in a vc...")


"""Helldiver Commands"""
@tree.command(
    name="getplanetstats",
    description="Returns the planet statistics from the helldivers 2 api"
)


@caliente.event
async def get_planet(interaction: discord.Interaction, planetname: str):

    getting_planet = requests.get("https://helldivers-2.fly.dev/api/801/planets")
    planets = getting_planet.json()
    found = False
    if planetname is None:
        await interaction.response.send_message("Please provide a planet name.")
        return
    for planet in planets:
        if planet["name"].lower() == planetname.lower():
            await interaction.response.send_message(f"Found planet! Getting planet info...")
            getting_planet_status = requests.get(f"https://helldivers-2.fly.dev/api/801/planets/{planet['index']}/status")  
            if getting_planet_status.status_code != 200:
                await interaction.response.send_message("An error occurred while trying to get the planet status.")
                return
            planet_status = getting_planet_status.json()
            embed_var = discord.Embed(title=f"Planet information for {planet["name"]}", color=discord.Color.blue())
            embed_var.add_field(name="Liberation status", value=planet_status["liberation"], inline=False)
            embed_var.add_field(name="Owner", value=planet_status["owner"], inline=False)
            embed_var.add_field(name="Sector", value=planet_status["planet"]["sector"], inline=False)
            embed_var.add_field(name="Active Players", value=planet_status["players"], inline=False)
            found = True
            await interaction.followup.send(embed=embed_var)
            print(planet["index"])
            break
    if not found:
        await interaction.response.send_message("Not found")
@tree.command(
    name="getevents",
    description="Returns current events from helldivers 2"
)

@caliente.event

async def getevents(interaction: discord.Interaction):
    getting_events = requests.get("https://helldivers-2.fly.dev/api/801/events")
    events = getting_events.json()
    event_embed = discord.Embed(title="Current events", color=discord.Color.red())
    if events == [""]:
        await interaction.response.send_message("No events found")
        return
    for event in events:
        event_embed.add_field(name=event["title"], value=event["message"]["en"], inline=False)
    await interaction.response.send_message(embed=event_embed)

@tree.command(
    name="galaxystats",
    description="Returns the galaxy statistics from helldivers 2"
)

@caliente.event

async def galaxystats(interaction: discord.Interaction):
    getting_galaxy = requests.get("https://api-hellhub-collective.koyeb.app/api/statistics/galaxy")
    galaxy = getting_galaxy.json()
    galaxy_embed = discord.Embed(title="Galaxy statistics", color=discord.Color.green())
    galaxy_embed.add_field(name="Missions Won", value=galaxy["data"]["missionsWon"], inline=False)
    galaxy_embed.add_field(name="Missions Lost", value=galaxy["data"]["missionsLost"], inline=False)
    galaxy_embed.add_field(name="Terminids Killed", value=galaxy["data"]["bugKills"], inline=False)
    galaxy_embed.add_field(name="Automatons Killed", value=galaxy["data"]["automatonKills"], inline=False)
    galaxy_embed.add_field(name="Illuminates Killed", value=galaxy["data"]["illuminateKills"], inline=False)
    galaxy_embed.add_field(name="Deaths", value=galaxy["data"]["deaths"], inline=False)
    galaxy_embed.add_field(name="Friendly Kills", value=galaxy["data"]["friendlyKills"], inline=False)
    await interaction.response.send_message(embed=galaxy_embed)

"""AI Commands"""
@tree.command(
    name="gemini",
    description="AI output from google gemini"
)

@caliente.event
async def gemini(interaction: discord.Interaction, message: str, image_url: str = None):
    if image_url is None:
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))
        model = genai.GenerativeModel(model_name="gemini-1.0-pro")
        response = model.generate_content(message)
        await interaction.response.send_message(response.text)
    else:
        response = requests.get(image_url)
        if response.status_code != 200:
            await interaction.response.send_message("An error occurred while trying to get the image.")
            return
        image = Image.open(BytesIO(response.content))

        genai.configure(api_key=os.getenv("GENAI_API_KEY"))
        model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest")
        prompt_parts = [
            image,
            message
        ]
        response = model.generate_content(prompt_parts)
        await interaction.response.send_message(response.text)
        print(response.text)
"""Developer Commands"""
@tree.command(
    name="evaluate",
    description="What does this do..."
)

@caliente.event
async def evaluate(interaction: discord.Interaction, code: str):
    local_variables = {
        "interaction": interaction,
        "caliente": caliente,
        "discord": discord,
        "requests": requests,
        "channel": interaction.channel,
        "author": interaction.user,
        "message": interaction.message,
        "guild": interaction.guild,
        "asyncio": asyncio,
        "time": time,
    }
    if interaction.user.id != 489061310022156302:
        await interaction.response.send_message("You don't have permission to use this command.")
        return
    try:
        exec(f"async def func():\n  return {code}", local_variables)
        result = await local_variables["func"]()
        try:
            await interaction.response.send_message(f"```{result}```")
        except discord.NotFound:
            await interaction.response.send_message(f"```{result}```")
    except Exception as e:
        try:
            await interaction.response.send_message(f"An error occurred while trying to evaluate the code: {e}")
        except discord.NotFound:
            await interaction.response.send_message(f"An error occurred while trying to evaluate the code: {e}")
            interaction.gui
@tree.command(
    name="reload",
    description="Reloads the bot"
)


@caliente.event
async def reload(interaction: discord.Interaction):
    if interaction.user.id != 489061310022156302:
        await interaction.response.send_message("You don't have permission to use this command.")
        return
    await interaction.response.send_message("Reloading bot...")
    os.execv(sys.executable, ['python'] + sys.argv)

@tree.command(
    name="serverlist",
    description="Lists all servers the bot is in"
)

@caliente.event
async def serverlist(interaction: discord.Interaction):
    if interaction.user.id != 489061310022156302:
        await interaction.response.send_message("You don't have permission to use this command.")
        return
    for guild in caliente.guilds:
        with open("servers.txt", "a") as f:
            f.write(f"{guild.name}: {guild.id}\n")
    await interaction.response.send_message(file=File("servers.txt"))
    sleep(2)
    print("Removed file")
    os.remove("servers.txt")

@tree.command(
    name="leave",
    description="Leaves a server"
)

@caliente.event

async def leave(interaction: discord.Interaction, guild_id: str):   
    if interaction.user.id != 489061310022156302:
        await interaction.response.send_message("You don't have permission to use this command.")
        return
    guild = caliente.get_guild(int(guild_id))
    if guild is None:
        await interaction.response.send_message("I'm not in that server.")
        return
    await guild.leave()
    await interaction.response.send_message(f"Left server {guild.name}")
@tree.command(
    name="leaveall",
    description="Leaves all the servers"
)

@caliente.event
async def leaveall(interaction: discord.Interaction):
    if interaction.user.id != 489061310022156302:
        await interaction.response.send_message("You don't have permission to use this command.")
        return
    view = discord.ui.View()
    style = discord.ButtonStyle.red
    item = discord.ui.Button(style=style, label="Do you want to do this???", custom_id="confirm")
    for i in range(10):
        i += 1
    if i == 10:
        interaction.response.send_message("10 Seconds has passed. Canceling action", ephemeral=True)
        return
    view.add_item(item)
    await interaction.response.send_message("Are you sure you want to leave all servers?", view=view)
    await interaction.followup.send("Leaving all servers...")
    for guild in caliente.guilds:
        await guild.leave()
        asyncio.sleep(1)
    print("Left all servers")
caliente.run(os.getenv("DISCORD_BOT_TOKEN"))
