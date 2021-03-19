import discord
import os
from discord.ext import commands, tasks
import logging
from datetime import date
import sqlite3
from random import randrange

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



token = os.getenv("DISCORD_BOT_TOKEN").strip()



bot = commands.Bot(command_prefix='pls ', description='comand mode',help_command=None)

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
    
    
def check_int(inputdata):
    try:
        int(inputdata)
        return True
    except ValueError:
        return False

def check_status(ctx):
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
    
    return status
    


def change_status(ctx, status):
    username = str(ctx.message.author)
    db = sqlite3.connect('vote.db')
    cursor = db.cursor()

    sql = '''
        SELECT * FROM users WHERE username = ?
        '''
    val = (username,)
    cursor.execute( sql , val)
    row_count = len(cursor.fetchall())
    logger.info('change_status ==================== : [{}]'.format(row_count))

    if  row_count > 0:
        sql = '''UPDATE users SET status = ?  
                    WHERE username=? '''
        val = (status, username)
        cursor.execute( sql , val)

        logger.info('change_status update ==================== : ')
    else:
        sql = '''INSERT INTO users (username, status)
                        VALUES(?,?)'''
        val = (username, status)
        cursor.execute( sql , val)
        logger.info('change_status insert ==================== : ')
    db.commit()
    db.close()


    
@bot.command()
async def help(ctx, *args):
    menu = ''' Some of the commands that you can use are:
        pls createvote
        pls createtitle
        pls createoptions
        pls poll
    
    '''
    await ctx.send(menu)
    
@bot.command()
async def title(ctx, *args):
    
    change_status(ctx, "title")
    await ctx.send('title [][] arguments: {}'.format(' '.join(args))) 
    
 
    



@bot.command()
async def test(ctx, *args):
    change_status(ctx, "test")
    logger.debug('test {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('test {} arguments: {}'.format(len(args), ', '.join(args)))  
    

@bot.command()
async def options(ctx, *args):
    change_status(ctx, "options")
    logger.debug('options {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('options {} arguments: {}'.format(len(args), ', '.join(args)))  
    
@bot.command()
async def votecontent(ctx, *args):
    logger.debug('votecontent {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send('votecontent {} arguments: {}'.format(len(args), ', '.join(args)))  

@bot.command()
async def adelle(ctx, *args):
    say = []
    say.append("You're lying")
    say.append("Hey")
    say.append("Mr. Choy")
    say.append("Hint")

    random_index = randrange(len(say))

    logger.debug('adelle {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send(say[random_index])  
    
@bot.command()
async def pauline(ctx, *args):
    say = []
    say.append("#6AMPauline")
    say.append("I am disapointed")
    say.append("I am confuzzled")

    random_index = randrange(len(say))

    logger.debug('adelle {} arguments: {}'.format(len(args), ', '.join(args)))
    await ctx.send(say[random_index]) 
    
@bot.command()
async def createvote(ctx, *args):
    change_status(ctx, "create")
    message = '''
    Type pls createtitle to make title \nType pls createoptions to make options \nType pls cancel to cancel
    '''
    await ctx.send(message) 
@bot.command()
async def vote(ctx, *args):
    msg_array = []
    username = str(ctx.message.author)
    print_votes = ""
    db = sqlite3.connect('vote.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    msg_array.append("Usage: 'pls poll option#' ")      
    title_sql = '''
    
    SELECT Title, id FROM vote 
    WHERE end = 0 AND 
        start_date <= datetime('now','localtime') AND 
        end_date >= datetime('now','localtime'); 
    '''
    cursor.execute(title_sql)
    vid = ""
    user_results = cursor.fetchall()
    for result in user_results:
        title = "Title: " + result['title']
        msg_array.append(title)
        vid = result['id']
        break

        
    options_sql = '''
    SELECT option_title, oid FROM option 
    WHERE vid = ? 
    '''
    cursor.execute(options_sql, (vid,))
    on_results = cursor.fetchall()
    
    
    for result in on_results:
        #logger.info('option_title ========================={} '.format(result['option_title']))
        #logger.info('option_id ========================={} '.format(result['oid']))
        concatinated = f" {result['oid']}: {result['option_title']}"
        msg_array.append(concatinated)
    
    db.commit()
    db.close()
    change_status(ctx, "voting")
    
    await ctx.send("\n".join(msg_array))
'''    
@bot.listen()
async def on_message(message):     
    print("on message")
'''    
    
@bot.command()
async def poll(ctx, *args):
    if len(args) == 1:
        logger.info("here")
        if check_int(args)
            logger.info("here2")
            if check_status(ctx) == "voting":
                await ctx.send(args)
            else:
                await ctx.send("Do 'pls vote' first!")
        else:
            await ctx.send("Input option number\nUsage: 'pls poll option#'")
    else:
        await ctx.send("Usage: 'pls poll option#'")
    
        
@bot.command()
async def quit(ctx, *args):
    change_status(ctx, "none")
bot.run(token)
