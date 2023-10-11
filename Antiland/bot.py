import aiohttp
from Antiland.message_updater import MessageUpdater
from Antiland.dialogue import Dialogue
from Antiland.account import Account
from Antiland.user import User
class Bot:
    """
    This is a brief description of what the function does.

    :param arg1: Description of arg1
    :type arg1: Type of arg1
    :param arg2: Description of arg2
    :type arg2: Type of arg2
    :return: Description of the return value
    :rtype: Type of the return value
    """
    def __init__(self, prefix, dialogue, session_token=None):
        self.prefix = prefix
        self.running = False
        self.token = None
        self.session_token = session_token
        self.message_updater = None
        self.commands = {}
        self.dialogue = None
        self.chats = {}
        self.dialogue = dialogue
        self.url = f"https://ps.pndsn.com/v2/subscribe/sub-c-24884386-3cf2-11e5-8d55-0619f8945a4f/{self.dialogue}/0?heartbeat=300&tt=16925582152759863&tr=42&uuid=0P3kmjSyFv&pnsdk=PubNub-JS-Web%2F4.37.0"

    async def process_message(self, message, token):
        if str(message).startswith(self.prefix):
            parts = message[len(self.prefix):].split(" ")
            if len(parts) >= 1:  # Check if there is at least one part (the command itself)
                command = parts[0]
                if len(parts) >= 2:  # Check if there is a parameter
                    param = parts[1]
                else:
                    param = None  # No parameter provided
                if command in self.commands:
                    if param is not None:
                        await self.commands[command](param)
                    else:
                        await self.commands[command]()

    async def start(self, token, selfbot=False):
        if token:
            login = await self.login(token)
            main_username = login[2]
            self.message_updater = MessageUpdater(self.url, main_username, self.process_message, selfbot)
            await self.message_updater.run(selfbot)

    async def login(self, token):
        url = "https://mobile-elb.antich.at/users/me"
        json_data = {
            "_method": "GET",
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                if response.status == 200:
                    user_data = await response.json()
                    username = user_data.get("profileName", "N/A")
                    gender = user_data.get("female", "N/A")
                    if gender:
                        emoji = "🚺"
                    else:
                        emoji = "🚹"
                    main_name = f"{username} {emoji}"
                    print("Logged in as {}".format(username))
                    return (username, gender, main_name)

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func

        return decorator

    async def update_profile(self, session_token, **kwargs):
        base_url = 'https://mobile-elb.antich.at/classes/_User/mV1UqOtkyL'
        common_data = {
            "_method": "PUT",
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": session_token
        }

        payload = common_data.copy()
        payload.update(kwargs)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(base_url, json=payload) as response:
                    if response.status == 200:
                        print("Profile update successful.")
                    else:
                        print(f"Profile update failed with status code {response.status}.")
                        print(await response.text())
        except Exception as e:
            print(f"Error: {e}")

    async def stats(self, session_token):
        url = "https://mobile-elb.antich.at/users/me"
        json_data = {
            "_method": "GET",
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "76b2aae2-0087-83e5-b86a-1a6d8ab69618",
            "_SessionToken": session_token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        account = Account(user_data)
                        return account
                    else:
                        return None
        except Exception as e:
            print(f"Error: {e}")

    async def translate(self, token, message, message_id):
        url = "https://mobile-elb.antich.at/functions/translateMessage"
        json_data = {
            "text": message,
            "messageId": message_id,
            "persist": True,
            "lang": "en",
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "76b2aae2-0087-83e5-b86a-1a6d8ab69618",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data) as translate:
                    translated = await translate.json()
                    result = translated.get("result")
                    return result
        except Exception as e:
            print(f"Error: {e}")

    async def get_contacts(self, token):
        url = "https://mobile-elb.antich.at/functions/getContacts"
        json_payload = {
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    data = await r.json()
                    users = [User(user_data) for user_data in data["result"]]
                    return users
        except Exception as e:
            print(f"Error: {e}")

    async def add_contact(self, uuid, token):
        url = "https://www.antichat.me/uat/parse/functions/addContact"
        json_payload = {
            "contact": uuid,
            "v": 10001,
            "_ApplicationId": "VxfAeNw8Vuw2XKCN",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "23b9f34b-a753-e248-b7c2-c80e38bc3b40",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    pass
        except Exception as e:
            print(f"Error: {e}")

    async def delete_contact(self, uuid, token):
        url = "https://mobile-elb.antich.at/functions/deleteContact"
        json_payload = {
            "contact": uuid,
            "v": 10001,
            "_ApplicationId": "VxfAeNw8Vuw2XKCN",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "23b9f34b-a753-e248-b7c2-c80e38bc3b40",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    pass
        except Exception as e:
            print(f"Error: {e}")

    async def block_user(self, uuid, token):
        url = "https://mobile-elb.antich.at/functions/BlockPrivate"
        json_payload = {
            "blockedId": uuid,
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    pass
        except Exception as e:
            print(f"Error: {e}")

    async def unblock_user(self, uuid, token):
        url = "https://mobile-elb.antich.at/functions/UnblockPrivate"
        json_payload = {
            "blockedId": uuid,
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    pass
        except Exception as e:
            print(f"Error: {e}")

    async def get_dialogue(self, dialogue, token):
        url = "https://mobile-elb.antich.at/functions/getDialogue"
        json_payload = {
            "dialogueId": dialogue,
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    data = await r.json()
                    dialogue = Dialogue(data["result"])
                    return dialogue
        except Exception as e:
            print(f"Error: {e}")
    
    async def get_topchats(self, token):
        url = "https://mobile-elb.antich.at/functions/getTopChats"
        json_payload = {
            "laterThen": {
              "iso": "2021-01-31T22:55:08.931Z",
              "__type": "Date"
            },
            "searchText": "",
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    data = await r.json()
                    dialogues = [Dialogue(dialogue) for dialogue in data["result"]]
                    return dialogues
        except Exception as e:
            print(f"Error: {e}")

    async def join_chat(self, token, dialogue):
        url = "https://mobile-elb.antich.at/functions/joinGroupChat"
        json_payload = {
            "chat": dialogue,
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    data = await r.json()
        except Exception as e:
            print(f"Error: {e}")

    async def exit_chat(self, token, dialogue):
        url = "https://mobile-elb.antich.at/functions/exitGroupChat"
        json_payload = {
            "chat": dialogue,
            "v": 10001,
            "_ApplicationId": "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5",
            "_ClientVersion": "js1.11.1",
            "_InstallationId": "3e355bb2-ce1f-0876-2e6b-e3b19adc4cef",
            "_SessionToken": token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as r:
                    data = await r.json()
        except Exception as e:
            print(f"Error: {e}")