from config.bot_config import BotConfig
import time
from twitchio.ext import commands
import requests
import aiohttp
import src.JsonDB as JsonDB

class Bot(commands.Bot):
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
        self.config = BotConfig()
      
        self._Isreq_Apex = False
        self.ID = ''
        self.Channel_Data={}
        self.Token = {}
        self._Isreq_Valorant = False
        self.nowTime_apex = time.time()
        self.nowTime_valorant = time.time()
        self.apex_data_api = None
        self.valorant_data_api = None
        self.database = JsonDB.read_json(
            filename='./src/jsonfile/database.json')
        super().__init__(
            token=self.config.TMI_TOKEN,
            prefix=self.config.BOT_PREFIX,
            initial_channels=self.config.CHANNEL,
        )

    async def get_game_tag(self, ID):

        url = f"https://api.twitch.tv/helix/channels?broadcaster_id={ID}"

        payload = {}
        headers = self.Token
        response = requests.request(
            "GET", url, headers=headers, data=payload).json()
        result = response["data"][0]["game_name"]

        return result

    async def command_read_database(self, Input_command, user_name, database):
        if Input_command in database['command']:
            commandp = database['command'][Input_command]
            command = commandp.split()
            command_str = ""
            for v in command:
                try:
                    if v == 'print':
                        command_str += f'message.channel.send(\' '
                    elif v == 'to':
                        command_str += f' @'
                    elif v == 'user':
                        command_str += f'{user_name}'
                    elif v == '{game_name}':
                        command_str += f'{await self.get_game_tag(self.ID)}'
                    elif v == 'end':
                        command_str += '\')'
                    else:
                        command_str += f' {v}'
                except Exception as e:
                    command_str = f'ctx.send({e})'
            return command_str

    async def event_ready(self):
        self.Token = await self.update_token(self.config.CLIENT_ID, self.config.SECRET)
        self.Channel_Data = await self.get_channel_data(self.config.CHANNEL)
        self.ID=self.Channel_Data["id"]
        print(
            f'Logged in as | {self.nick} To ==> {"".join(self.config.CHANNEL)}')

    async def event_message(self, message):
        if message.echo:
            return
        msg = message.content
        name = message.author.name
        print(msg + "<=====" + name)
        if msg.startswith('$'):
            if msg[1:] in self.database['command']:
                try:
                    await eval(await self.command_read_database(msg[1:], name, self.database))
                except:
                    pass
            ################################################
            elif msg.split('@')[0][1:] == 'add':
                if name in self.config.ADMIN:
                    try:
                        self.database['command'].update(
                            {msg.split("@")[1]: msg.split("@")[2]})
                        JsonDB.write_json(
                            filename='./src/jsonfile/database.json', data=self.database)
                        await message.channel.send(f'add command {msg.split("@")[1]} done!!')
                    except:
                        await message.channel.send(f'add command {msg.split("@")[1]} failed!!')
        await self.handle_commands(message)

    async def event_join(self, channel, user):
        if user.name  in self.database["User"]:
            await self.connected_channels[0].send(f"?????????????????? {self.database['User'][user.name]} ????????????????????????????????????????????????????????? Chat {self.config.CHANNEL[0]} || @{user.name} ")
    async def update_token(self, c_id_, c_secret_):
        body = {
            'client_id': c_id_,
            'client_secret': c_secret_,
            "grant_type": 'client_credentials'
        }
        r = requests.post('https://id.twitch.tv/oauth2/token', body)
        keys = r.json()
        headers = {
            'Client-ID': c_id_,
            'Authorization': 'Bearer ' + keys['access_token']
        }
        return headers

    # function to get twitch channel id
    async def get_channel_data(self, channel_name):
        url = f"https://api.twitch.tv/helix/users?login={''.join(channel_name)}"

        payload = {}
        headers = self.Token

        response = requests.request(
            "GET", url, headers=headers, data=payload).json()
        result = response["data"][0]

        return result

   

   

    @commands.command(name="python", aliases=['py'])
    async def Python(self, ctx: commands.Context, *, msg: str):
        if ctx.author.name in self.config.ADMIN:
            try:
                try:
                    await eval(f" ctx.send({msg})")
                except:
                    try:
                        await eval(f" ctx.send(str({msg}))")
                    except Exception as e:
                        await ctx.send(f"error: {e}")
            except:
                await ctx.send("input some code!!")
        else:
            await ctx.send("You are not LalaBot Admin")

    # add so command
    @commands.command(name="so")
    async def so(self, ctx: commands.Context, *, msg: str):
        data = await self.get_channel_data(msg)
        # only for brodcaster
        if ctx.author.name in self.config.ADMIN or ctx.author.name == self.config.CHANNEL[0]:
           await ctx.send(
                f'{msg} is now streaming on {f"https://www.twitch.tv/{msg}"} || description ==> {data["description"]}::GAME ==> {await self.get_game_tag(data["id"])} ????????????????')
    @commands.command(name="register", aliases=['reg','regist'])
    async def register(self, ctx: commands.Context, *, msg: str):
            self.database['User'].update({ctx.author.name:msg})
            JsonDB.write_json(
                filename='./src/jsonfile/database.json', data=self.database)
            await ctx.send(f'??????????????????????????? {msg} ??????????????????!!')
    #name check command
    @commands.command(name="namecheck", aliases=['nc'])
    async def namecheck(self, ctx: commands.Context):
        if ctx.author.name in self.database['User']:
            await ctx.send(f'?????????????????? {self.database["User"][ctx.author.name]} ????????????????????????????????????????????????????????? Chat ????????? {self.config.CHANNEL[0]}')
        else:
            await ctx.send(f'?????????command !reg ???????????????????????????????????????????????????')

bot = Bot()
bot.run()
