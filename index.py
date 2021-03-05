import discord
import os
from discord.ext import commands, tasks
import logging
from datetime import date
import sqlite3

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



token = os.getenv("DISCORD_BOT_TOKEN").strip()



bot = commands.Bot(command_prefix='pls ', description='comand mode')

date = date.today()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=""))
    
    print('Voting Bot is online!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{error}')
        
@bot.event
async def on_member_join(member):
    logger.info(f'{member} has joined the server on ' + str(date))
    
@bot.event
async def on_member_remove(member):
    logger.info(f'{member} has left the server on ' + str(date))
    
@bot.command()
async def title(ctx, *args):
    username = str(ctx.message.author)
    
    db = sqlite3.connect('vote.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user_results = cursor.fetchall()
    db.commit()
    db.close()
    for result in user_results:
        status = result['status']
        break
    logger.info('title {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('title [{}][{}] arguments: {}'.format(username, status, ' '.join(args))) 
    

@bot.command()
async def test(ctx, *args):
    logger.debug('test {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('test {} arguments: {}'.format(len(args), ', '.join(args)))  
    

@bot.command()
async def options(ctx, *args):
    logger.debug('options {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('options {} arguments: {}'.format(len(args), ', '.join(args)))  
    
@bot.command()
async def votecontent(ctx, *args):
    logger.debug('votecontent {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('votecontent {} arguments: {}'.format(len(args), ', '.join(args)))  

bot.run(token)
