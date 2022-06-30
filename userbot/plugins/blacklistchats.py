from datetime import datetime

from telethon.utils import get_display_name

from userbot import catub
from userbot.core.logger import logging

from ..core.data import blacklist_chats_list
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import global_collectionjson as sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "tools"

LOGS = logging.getLogger(__name__)


@catub.cat_cmd(
    pattern="chatblacklist (on|off)$",
    command=("chatblacklist", plugin_category),
    info={
        "header": "To enable and disable chats blacklist",
        "description": "If you turn this on , then your userbot won't work on the chats stored\
         in database by addblackchat command ! If you turn it off even though you added chats to database\
         userbot won't stop working in that chat",
        "usage": "{tr}chatblacklist <on/off>",
    },
)
async def chat_blacklist(event):
    "To enable and disable chats blacklist"
    input_str = event.pattern_match.group(1)
    blkchats = blacklist_chats_list()
    if input_str == "on":
        if gvarstatus("blacklist_chats") is not None:
            return await edit_delete(event, "Already it was turned on")
        addgvar("blacklist_chats", "true")
        text = "From now on , your cat userbot doesn't work in the chats stored in database"
        if len(blkchats) != 0:
            text += (
                "Bot is reloading to apply the changes please wait for a minute"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        text += "You haven't added any chat to blacklist"
        return await edit_or_reply(
            event,
            text,
        )
    if gvarstatus("blacklist_chats") is not None:
        delgvar("blacklist_chats")
        text = "Your cat userbot is as free as a bird ! It works in every chat"
        if len(blkchats) != 0:
            text += (
                "Bot is reloading to apply the changes please wait for a minute"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        text += "You haven't added any chat to blacklist"
        return await edit_or_reply(
            event,
            text,
        )
    await edit_delete(event, "It was turned off already")


@catub.cat_cmd(
    pattern="addblkchat(s)?(?:\s|$)([\s\S]*)",
    command=("addblkchat", plugin_category),
    info={
        "header": "To add chats to blacklist",
        "description": "To add the chats to database so your bot doesn't work in\
         those chats either give chat ids as input or do this command in the chat\
         which you want to add to db",
        "usage": [
            "{tr}addblkchat <chat ids>",
            "{tr}addblkchat in the chat which you want to add",
        ],
    },
)
async def add_blacklist_chat(event):
    "To add chats to blacklist"
    input_str = event.pattern_match.group(2)
    errors = ""
    result = ""
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if input_str:
        input_str = input_str.split(" ")
        for chatid in input_str:
            try:
                chatid = int(chatid.strip())
                if chatid in blkchats:
                    errors += f"While adding the {chatid} - This chat has already been blacklisted\n"
                    continue
                chat = await event.client.get_entity(chatid)
                date = str(datetime.now().strftime("%B %d, %Y"))
                chatdata = {
                    "chat_id": chat.id,
                    "chat_name": get_display_name(chat),
                    "chat_username": chat.username,
                    "date": date,
                }
                blacklistchats[str(chat.id)] = chatdata
                result += (
                    f"Successfully added {get_display_name(chat)} to blacklist chats\n"
                )
            except Exception as e:
                errors += f"While adding the {chatid} - {e}\n"
    else:
        chat = await event.get_chat()
        try:
            chatid = chat.id
            if chatid in blkchats:
                errors += f"While adding the {chatid} - This chat has already been blacklisted\n"
            else:
                date = str(datetime.now().strftime("%B %d, %Y"))
                chatdata = {
                    "chat_id": chat.id,
                    "chat_name": get_display_name(chat),
                    "chat_username": chat.username,
                    "date": date,
                }
                blacklistchats[str(chat.id)] = chatdata
                result += (
                    f"Successfully added {get_display_name(chat)} to blacklist chats\n"
                )
        except Exception as e:
            errors += f"While adding the {chatid} - {e}\n"
    sql.del_collection("blacklist_chats_list")
    sql.add_collection("blacklist_chats_list", blacklistchats, {})
    output = ""
    if result != "":
        output += f"Success :\n{result}\n"
    if errors != "":
        output += f"Error :\n{errors}\n"
    if result != "":
        output += "Bot is reloading to apply the changes please wait for a minute"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="rmblkchat(s)?(?:\s|$)([\s\S]*)",
    command=("rmblkchat", plugin_category),
    info={
        "header": "To remove chats to blacklist",
        "description": "To remove the chats from database so your bot will work in\
         those chats either give chatids as input or do this command in the chat\
         which you want to remove from db",
        "usage": [
            "{tr}rmblkchat <chat ids>",
            "{tr}rmblkchat in the chat which you want to add",
        ],
    },
)
async def add_blacklist_chat(event):
    "To remove chats from blacklisted chats"
    input_str = event.pattern_match.group(2)
    errors = ""
    result = ""
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if input_str:
        input_str = input_str.split(" ")
        for chatid in input_str:
            try:
                chatid = int(chatid.strip())
                if chatid in blkchats:
                    chatname = blacklistchats[str(chatid)]["chat_name"]
                    del blacklistchats[str(chatid)]
                    result += (
                        f"Successfully removed {chatname} from blacklisted chats\n"
                    )
                else:
                    errors += f"The given id {chatid} doesn't exists in your database ! That is it hasn't been blacklisted\n"
            except Exception as e:
                errors += f"While removing the {chatid} - {e}\n"
    else:
        chat = await event.get_chat()
        try:
            chatid = chat.id
            if chatid in blkchats:
                chatname = blacklistchats[str(chatid)]["chat_name"]
                del blacklistchats[str(chatid)]
                result += f"Successfully removed {chatname} from blacklisted chats\n"
            else:
                errors += f"The given id {chatid} doesn't exists in your database ! That is it hasn't been blacklisted\n"
        except Exception as e:
            errors += f"While removing the {chatid} - {e}\n"
    sql.del_collection("blacklist_chats_list")
    sql.add_collection("blacklist_chats_list", blacklistchats, {})
    output = ""
    if result != "":
        output += f"Success :\n{result}\n"
    if errors != "":
        output += f"Error :\n{errors}\n"
    if result != "":
        output += "Bot is reloading to apply the changes please wait for a minute"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="listblkchats$",
    command=("listblkchats", plugin_category),
    info={
        "header": "To list all blacklisted chats",
        "description": "Will show you the list of all blacklisted chats",
        "usage": [
            "{tr}listblkchat",
        ],
    },
)
async def add_blacklist_chat(event):
    "To show list of chats which are blacklisted"
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if len(blkchats) == 0:
        return await edit_delete(
            event, "There are no blacklisted chats in your bot"
        )
    result = "The list of blacklisted chats are :\n\n"
    for chat in blkchats:
        result += f"{blacklistchats[str(chat)]['chat_name']}\n\n"
        result += f"Chat id : `{chat}`\n\n"
        username = blacklistchats[str(chat)]["chat_username"] or "Private group"
        result += f"Username : {username}\n\n"
        result += f"Added on {blacklistchats[str(chat)]['date']}\n\n"
    await edit_or_reply(event, result)
