import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv
import os


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_NEO_BOT_TOKEN")

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store active voice clients
voice_clients = {}

@bot.event
async def on_ready():
    print(f"NEO BOT is online as {bot.user.name}!")
    activity = discord.Game(name="Streaming music from YouTube!")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        voice_clients[ctx.guild.id] = voice_client
        await ctx.send(f"🎶 NEO BOT joined the voice channel: **{channel.name}**!")
    else:
        await ctx.send("⚠️ Join a voice channel first!")

@bot.command()
async def leave(ctx):
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        await ctx.send("👋 NEO BOT left the voice channel.")
    else:
        await ctx.send("⚠️ NEO BOT is not connected to any voice channel!")

@bot.command()
async def play(ctx, url: str):
    if ctx.guild.id not in voice_clients:
        await ctx.send("⚠️ Use `!join` to connect to a voice channel first!")
        return

    voice_client = voice_clients[ctx.guild.id]

    if voice_client.is_playing():
        await ctx.send("⚠️ Already playing music. Use `!stop` to stop the current playback.")
        return

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]
            title = info.get("title", "Unknown Title")

        source = discord.FFmpegPCMAudio(audio_url, executable="ffmpeg")
        voice_client.play(source, after=lambda e: print(f"Error: {e}") if e else None)
        await ctx.send(f"🎶 Now playing: **{title}**")
    except Exception as e:
        await ctx.send("⚠️ Could not play the audio. Check the YouTube link!")
        print(f"Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
        voice_clients[ctx.guild.id].stop()
        await ctx.send("⏹️ Music playback stopped.")
    else:
        await ctx.send("⚠️ No music is currently playing.")

bot.run(DISCORD_TOKEN)
