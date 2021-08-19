from bs4 import BeautifulSoup
from discord import user
import feedparser
import discord
import asyncio
import urllib  #imports obv

rss_url = 'https://www.mangaupdates.com/rss.php'                                #MU rss-url
readlist_url = 'YOUR READ LIST'   #url of your readlist
global read_lst
global link_lst
read_lst = []
link_lst = []

def readlist():
    content = urllib.request.urlopen(readlist_url)
    read_content = content.read()
    soup = BeautifulSoup(read_content,'html.parser')   #scrape html of readlist page
    followT = soup.find_all(title='Series Info')      #series titles
    links = [a.get('href') for a in soup.find_all('a', href=True)]  #all links

    for ele in followT:
        read_lst.append(ele.text)  #put all titles in list

    for ele in links:
        if 'series.html?id' in ele:
            link_lst.append(ele)      #all series links in list

readlist()

class MyClient(discord.Client): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.feedupdate())  #i dont get any of this
    
    async def on_ready(self):
        print('Connected!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user)) #ready message

    async def feedupdate(self):   #main function                
        await self.wait_until_ready()
        channel = self.get_channel(YOUR CHANNEL ID)   #channel id of updates
        lst_of_msg = []
        while not self.is_closed():
            d = feedparser.parse(rss_url)         #parse rss feed
            messages = await channel.history(limit=100).flatten()
            for ele in messages:
                lst_of_msg.append(ele.content)          #list of message history
            for item in d.entries:
                if not any(ele in item.title for ele in lst_of_msg):
                    if any(ele in item.link for ele in link_lst):
                        await channel.send(item.title) #send title if tile is not in message history and it does appear in linklst
            lst_of_msg = []                     #empty message history list
            await asyncio.sleep(60)                  #timer
    
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!check'):         #on command '!check' send back 'checked'
            await message.channel.send('checked')   

        if message.content.startswith('!list'):          #on command '!list' send back readlist 
            sep = '\n'
            x = sep.join(read_lst)
            userlist = discord.Embed(
                title = 'Your reading list',
                url = readlist_url,
                description = x
            )

            userlist.set_author(name = 'MangaUpdates', url = 'https://www.mangaupdates.com/index.html')
            # userlist.set_footer(text = link_lst)
            await message.channel.send(embed=userlist)
        
        if message.content.startswith('!updatelist'):      #on command '!updatelist' update the readlist
            read_lst.clear()
            link_lst.clear()
            readlist()
            await message.channel.send('List updated!')
    

                    
client = MyClient()
client.run('YOUR TOKEN')
