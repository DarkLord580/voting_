import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        
        # don't respond to ourselves
        if message.author == self.user:
            return

        elif message.content == 'pls createvote':
            await message.channel.send('1.input tite\n2.input options\n Press 3 to cancel')
        elif message.content == '1':
            await message.channel.send('What\'s the title?')
        elif message.content == '3':
            await message.channel.send('Canceled.')   
        else:
            await message.channel.send('Confirmed')
client = MyClient()
client.run('ODEzNjU4NDI5NTU3NzAyNjU2.YDSgdg.XZFWXmr8k6BFJgpOnUia7zy0uL8')