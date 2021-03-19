import discord
import os
from discord.ext import commands, tasks
import logging
from datetime import date
import sqlite3
from random import randrange

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

token = os.getenv("DISCORD_BOT_TOKEN").strip()

bot = commands.Bot(command_prefix='pls ', description='comand mode',help_command=None)
date = date.today()

def check_status(ctx):
    username = str(ctx.message.author)

    db = sqlite3.connect('vote.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user WHERE username=?', (username,))
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
        SELECT status FROM user WHERE username = ?
        '''
    val = (username,)
    cursor.execute( sql , val)
    results = cursor.fetchall()
    row_count = len(results)
    
    if  row_count > 0:
        for result in results:
            select_status = result[0]
            break
        
        logger.debug('change_status compare ==================== :[{}]'.format(select_status != status))
        if select_status != status:
            sql = '''UPDATE user SET status = ?  
                        WHERE username=? '''
            val = (status, username)
            cursor.execute( sql , val)
        logger.debug('change_status updated ==================== :[{}]'.format(status))
        
    else:
        logger.debug('change_status row_count <=0 ==================== :[{}]'.format(row_count))
        sql = '''INSERT INTO user (username, status)
                        VALUES(?,?)'''
        val = (username, status)
        cursor.execute( sql , val)
        logger.debug('change_status inserted ==================== :[{}]'.format(status))
    db.commit()
    db.close()

def insert_title(ctx, username, user_status, title):
   
    vid = -1
    if user_status == 'create':
        db = sqlite3.connect('vote.db')
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        '''checking select vote for creating'''

        vote_sql = '''
        INSERT INTO vote (username, title, create_date)
        VALUES (?,? , datetime('now','localtime') ); 
        '''
        cursor.execute(vote_sql, (username, title))
        logger.debug('insert_title ==================== :[{}]'.format(cursor.lastrowid))
        db.commit()
        db.close()
        vid = cursor.lastrowid
        change_status(ctx, f'{user_status}{cursor.lastrowid}')
    elif 'create' in user_status:
        vid = user_status.split("create",1)[1]
    return vid
    

def insert_option(ctx, user_status, option_title):

    logger.debug('insert_option user_status ============{}'.format(user_status))
    if 'create' in user_status:
        
        vid = user_status.split("create",1)[1]
        logger.debug('insert_option get VID ============{}'.format(vid))

        db = sqlite3.connect('vote.db')
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        

        option_sql = '''
        INSERT INTO option (vid, option_title, create_date)
        VALUES (?,? , datetime('now','localtime')); 
        '''
        results = cursor.execute(option_sql, (vid, option_title))
        db.commit()
        db.close()

def update_startdate(ctx, user_status, start_date):
    logger.debug('update_startdate user_status ============{}'.format(user_status))
    if 'create' in user_status:
        
        vid = user_status.split("create",1)[1]
        logger.debug('update_startdate get VID ============{}'.format(vid))

        db = sqlite3.connect('vote.db')
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        startdate_sql = '''
        UPDATE vote set start_date = ?
        WHERE id = ?; 
        '''
        results = cursor.execute(startdate_sql, (start_date, vid))
        db.commit()
        db.close()




@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=""))
    
    print('Voting Bot is online!')

@bot.event
async def on_command_error(ctx, error):
    logger.info(f"on_command_error ========{error}" )

    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{error}')

@bot.command(pass_context = True)
async def cookie(self, ctx):
    await self.bot.say("@{} :cookie:".format(ctx.message.author.id))
        
@bot.event
async def on_member_join(member):
    logger.info(f'{member} has joined the server on ' + str(date))
    
@bot.event
async def on_member_remove(member):
    logger.info(f'{member} has left the server on ' + str(date))
    
def validate_int(inputdata):
    try:
        int(inputdata)
        return True
    except ValueError:
        return False

def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        raise False


@bot.command()
async def help(ctx, *args):
    menu = ''' Usage:
        pls createvote
        pls poll
        pls quit
    
    '''
    await ctx.send(menu)

@bot.command()
async def create(ctx, *args):
    change_status(ctx, "create")
    message = '''Type pls title "title" to make title
Type pls options "option" to make options
Type pls startdate "startdate" to make startdate
Type pls enddate "enddate" to make enddate
Type pls finish to make finish
Type pls quit to cancel
    '''
    await ctx.send(message) 

@bot.command()
async def title(ctx, *args):

    len_args = len(args)

    logger.debug('createtitle ============{} arguments: {}'.format(len_args, ', '.join(args)))
    user_status = check_status(ctx)
    if user_status == "create":
        username = str(ctx.message.author)
        if len_args == 1:
            insert_title(ctx,username, user_status, args[0])
            await ctx.send(f'Title created: {args[0]}' )

        else:
            await ctx.send('Usage: pls title "title"' )
    elif 'create' in user_status:
        await ctx.send('Already Done' )
    else:
        await ctx.send('Do "pls create" first!!')


@bot.command()
async def options(ctx, *args):
    len_args = len(args)

    logger.debug('createoptions ============{} arguments: {}'.format(len_args, ', '.join(args)))
    user_status = check_status(ctx)
    logger.debug('createoptions user_status ============{} '.format(user_status))
    
    if user_status == "create":
        await ctx.send('Do "pls title" first!!')
    elif 'create' in user_status:
        if len_args == 1:
            insert_option(ctx,user_status,args[0])
            await ctx.send(f'Option created: {args[0]}' )
        else: 
            await ctx.send('Usage: pls options "title" ')
    else:
        await ctx.send('Do "pls create" first!!')
        
@bot.command()
async def startdate (ctx, *args):
    len_args = len(args)

    logger.debug('startdate ============{} arguments: {}'.format(len_args, ', '.join(args)))
    user_status = check_status(ctx)

    if user_status == "create":
        await ctx.send('Do "pls title" first!!')
    elif 'create' in user_status:
        ''' check arg[0]   validate_date'''
        if len_args == 1:
        
            if validate_date(args[0]) == True:
                update_startdate(ctx,user_status,args[0])
                await ctx.send(f'Startdate updated: {args[0]}' )
            else:
                await ctx.send(f'Usage: pls startdate  "YYYY-MM-DD"' )
        else: 
             await ctx.send('Usage: pls startdate "time" ')

    else:
        await ctx.send('Do "pls create" first!!')


@bot.command()
async def enddate (ctx, *args):
    len_args = len(args)

    logger.debug('enddate ============{} arguments: {}'.format(len_args, ', '.join(args)))
    user_status = check_status(ctx)
    if user_status == "create":
        username = str(ctx.message.author)
        if len_args == 1:
            insert_option(ctx,username, user_status, args[0])

        else:
            await ctx.send('Usage: pls enddate "enddate"' )

    else:
        await ctx.send('Do "pls create" first!!')


@bot.command()
async def finish (ctx, *args):
    logger.debug('finish ============')
    user_status = check_status(ctx)
    if user_status == "create":
        username = str(ctx.message.author)
        update_finish(ctx,username)
    else:
        await ctx.send('Do "pls create" first!!')


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
        msg_array.append(f"Title: {result['title']}")
        vid = result['id']
        break

        
    options_sql = '''
    SELECT option_title, oid FROM option 
    WHERE vid = ? 
    '''
    cursor.execute(options_sql, (vid,))
    on_results = cursor.fetchall()
    
    
    for result in on_results:
        logger.debug('option_title ========================={} '.format(result['option_title']))
        logger.debug('option_id ========================={} '.format(result['oid']))
        concatinated = f" {result['oid']}: {result['option_title']}"
        msg_array.append(concatinated)
    
    db.commit()
    db.close()
    change_status(ctx, "voting")
    logger.debug('msg_array ========================={} '.format("\n".join(msg_array)))
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
        if validate_int(args) == True:
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

@bot.command()
async def adelle(ctx, *args):

    adelle_sql = '''
    SELECT say FROM adelle_pauline
    WHERE is_adelle = 'Y'
    ORDER BY random() 
    LIMIT 1;
    '''
    
    db = sqlite3.connect('vote.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
   
    cursor.execute(adelle_sql)
    results = cursor.fetchall()

    for result in results:
        say = "Adelle says: " + result['say']
        break

    db.commit()
    db.close()

    logger.debug( f'pls adelle =========[{say}]')
    await ctx.send(say)  

@bot.command()
async def pauline(ctx, *args):
    adelle_sql = '''
    SELECT say FROM adelle_pauline
    WHERE is_adelle = 'N'
    ORDER BY random() 
    LIMIT 1;
    '''
    
    db = sqlite3.connect('vote.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
   
    cursor.execute(adelle_sql)
    results = cursor.fetchall()

    for result in results:
        say = "Pauline says: " + result['say']
        break

    db.commit()
    db.close()

    logger.debug( f'pls pauline =========[{say}]')
    await ctx.send(say)


bot.run(token)
