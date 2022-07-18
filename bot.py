import discord
from discord.ext import commands, tasks

import random
import dotenv

dotenv.load()

client = commands.Bot(command_prefix='$')

# How long to wait inbetween each scramble
SCRAMBLE_WAIT_TIME_SECONDS = 0
SCRAMBLE_WAIT_TIME_MINUTES = 0
SCRAMBLE_WAIT_TIME_HOURS = 2

# List of words file
WORDS_FILE = "words.txt"

guessed = False

# Read list of words from file
with open(WORDS_FILE, "r") as f:
    config = [x.strip() for x in f.readlines()]

@client.event
async def on_ready():
    print("Ready")

    # Start the scramble loop
    post_scramble.start()

@tasks.loop(hours=SCRAMBLE_WAIT_TIME_HOURS, minutes=SCRAMBLE_WAIT_TIME_MINUTES, seconds=SCRAMBLE_WAIT_TIME_SECONDS)
async def post_scramble():
    global word
    global scrambled
    global guessed
    global config

    guessed = False

    # Pick word from config list
    word = random.choice(config)
    word_list = list(word)

    # Shuffle the word
    random.shuffle(word_list)
    scrambled = ''.join(word_list)

    # Very Rare: Incase scrambled word is the same as the word
    while scrambled == word:
        random.shuffle(word_list)
        scrambled = ''.join(word_list)

    print(word, scrambled)

    # Send scramble to the #scramble channel. Replace the 998053657192960010 with your scramble channel id
    channel = client.get_channel(998053657192960010)
    embed = discord.Embed(title="Scramble", description=scrambled, color=discord.Color.blue())
    await channel.send(embed=embed)

@client.command()
async def guess_scramble(ctx, arg1):
    '''
    Guess the scramble. This command will show you what letters you got correct
    '''

    global word
    global guessed

    # Creating a list of the correct words that the user guessed
    guessed_list = []
    for _ in range(len(word)):
        guessed_list.append("_")

    # If the scramble has already been solved, tell them the scramble was already solved
    if guessed:
        embed = discord.Embed(title="Scramble", description="The Scramble Has Already Been Solved", color=discord.Color.blue())
        await ctx.send(embed=embed)
    
    # If the scramble is not solved and the user's guess is correct, tell them they got the scramble correct
    elif str(arg1).lower() == word:
        guessed = True
        embed = discord.Embed(title="Scramble Winner!", description=f"{ctx.author.mention} Gussed The Scramble!", color=discord.Color.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    # If the scramble is not solved and the user's guess is incorrect, tell them what letters were in the correct spot
    elif not guessed:
        # Calculating what letters were in the correct spot
        msg = str(arg1).lower()
        for i in range(len(msg)):
            for j in range(len(word)):
                if i == j and msg[i] == word[j]:
                    guessed_list[j] = word[j]

        # Appending those correct letters to a string with some fancy formating
        to_send = ""
        for i in range(len(guessed_list)):
            if guessed_list[i] != "_":
                to_send += guessed_list[i] + " "
            else:
                to_send += "\\_ "

        # Sending the string
        embed = discord.Embed(title="Scramble Guess", description=to_send, color=discord.Color.gold())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

@client.command()
async def scramble(ctx):
    '''
    Prints the current scramble
    '''

    # If the scramble hasn't been solved, send them the current scramble
    if not guessed:
        embed = discord.Embed(title="Scramble", description=scrambled, color=discord.Color.blue())
        await ctx.send(embed=embed)

    # If the scramble has been solved, then tell the user the scramble has already been solved
    else:
        embed = discord.Embed(title="Scramble", description="The Scramble Has Already Been Solved", color=discord.Color.blue())
        await ctx.send(embed=embed)

@client.event
async def on_message(message):
    global word
    global guessed

    if message.author != client.user:
        # If the guess was correct, then tell the user they guessed the scramble
        if str(message.content).lower() == word and not guessed:
            guessed = True
            embed = discord.Embed(title="Scramble Winner!", description=f"{message.author.mention} Gussed The Scramble!", color=discord.Color.red())
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

    # on_message blocks the processing of commands so we just process the commands in the on_message loop
    await client.process_commands(message)

client.run(dotenv.get("SCRAMBLE_TOKEN"))