from chatgpt_wrapper import ChatGPT
from dotenv import load_dotenv
import os, subprocess
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, ChatMessage, EventData, ChatCommand
import asyncio
import json
  
# Opening JSON file
f = open('data.json', 'r')
  
# returns JSON object as 
# a dictionary
data = json.load(f)

load_dotenv()

#auth stuff
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]


# create instance of twitch API and create app authentication
twitch = Twitch(client_id, client_secret)


#asks chatgpt for a response, prints it out
def test(message):
    bot = ChatGPT()
    response = bot.ask(message)
    print("ChatGPT: " + response)
    bot._cleanup()
    return response
 
# use !emulate in twitch chat to call this
# compiles messages from data.json and asks ChatGPT to generate a response base on them
async def emulate_command_handler(cmd: ChatCommand):
    f2 = open('data.json', 'r')
    newData = json.load(f2)

    user_name = cmd.user.name
    # print("parameter: ", cmd.parameter)
    if (cmd.parameter != ''):
        user_name = cmd.parameter.lower()
            
    if(user_name not in newData):
        await cmd.reply(cmd.parameter + " doesn't have enough messages")
        return
    

    messageList = newData[user_name]['messages']
    promptString = 'Generate a message under 500 characters written with the personality of someone who said: '
    for message in messageList:
        promptString += "\""+message+"\","

    promptString = promptString[:-1] # remove the last character

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, test, promptString)
    replyName = cmd.user.name
    if(cmd.parameter != ''):
        replyName = cmd.parameter

    response = (response[:497] + '...') if len(response) > 500 else response

    await cmd.reply(replyName + " be like: " + response)
    return

        # await cmd.reply(f'{cmd.user.name} asked me to say \"{cmd.parameter}\"')


async def emaulte_command_handler(cmd: ChatCommand):
    f2 = open('data.json', 'r')
    newData = json.load(f2)

    user_name = cmd.user.name
    # print("parameter: ", cmd.parameter)
    if (cmd.parameter != ''):
        user_name = cmd.parameter.lower()
            
    if(user_name not in newData):
        await cmd.reply(cmd.parameter + " doesn't have enough messages")
        return
    

    messageList = newData[user_name]['messages']
    promptString = 'Generate a message under 500 characters written with the the opposite personality of someone who said: '
    for message in messageList:
        promptString += "\""+message+"\","

    promptString = promptString[:-1] # remove the last character

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, test, promptString)
    replyName = cmd.user.name
    if(cmd.parameter != ''):
        replyName = cmd.parameter

    response = (response[:497] + '...') if len(response) > 500 else response

    await cmd.reply("Evil " + replyName + " be like: " + response)
    return 

# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room('ezra0110')
    # you can do other bot initialization things in here

# this will be called whenever a message in a channel was send by either the bot OR another user
# adds messages and their count to the data.json file
async def on_message(msg: ChatMessage):
    # print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    if(msg.text[0] == '!'):
        return
    print(f'{msg.user.name}: {msg.text}')
    user_name = msg.user.name
    if (user_name) in data:
        if(data[user_name]["numMessages"] >= 50):
            data[user_name]["messages"].pop()
        else:
            data[user_name]["numMessages"] += 1
        data[user_name]["messages"].append(msg.text)
    else:
        data[user_name] = {"numMessages": 1, "messages": [msg.text]}

    with open("data.json", "w") as outfile:
        json.dump(data, outfile)
    return
    # print(await ChatGPT().ask(msg.text))

# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(client_id, client_secret)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    # OAUTH_TOKEN, REFRESH_TOKEN = await auth.authenticate()
    await twitch.set_user_authentication(OAUTH_TOKEN, USER_SCOPE, REFRESH_TOKEN)

    # create chat instance
    chat = await Chat(twitch)

    # # register the handlers for the events you want

    # # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)


    # # you can directly register commands and their handlers, this will register the !reply command
    # chat.register_command('reply', test_command)

    # chat.register_command('say', say_command_handler)
    chat.register_command('emulate', emulate_command_handler)
    chat.register_command('emaulte', emaulte_command_handler)


    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()
        f.close()

# lets run our setup
asyncio.run(run())
# asyncio.run(chatGPT())

# bot = ChatGPT()
# response = bot.ask("Hello, world!")
# print(response)  # prints the response from chatGPT
