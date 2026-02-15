import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import re
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Moderation
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=False)
    await ctx.send(f'Muted {member.mention}')

@bot.command()
@commands.has_permissions(move_members=True)
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    await member.move_to(channel)
    await ctx.send(f'Moved {member.mention} to {channel.name}')

# Music
@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("You're not in a voice channel.")
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url2 = info['url']
            title = info['title']
        except:
            await ctx.send("Couldn't find that song.")
            return

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
    ctx.voice_client.play(source)
    await ctx.send(f"Now playing: {title}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and left voice channel.")

# TikTok/Instagram link reposter
def extract_video_url(link):
    ydl_opts = {'quiet': True, 'format': 'best[ext=mp4]'}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('url', None)
    except:
        return None

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    urls = re.findall(r'(https?://\S+)', message.content)
    for url in urls:
        if 'tiktok.com' in url or 'instagram.com' in url:
            video_url = extract_video_url(url)
            if video_url:
                await message.reply(f"📹 Direct video link: {video_url}")
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv('BOT_TOKEN')
    bot.run(token)
