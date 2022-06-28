# Copyright (C) 2019 The Raphielscape Company LLC.
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
# catUserbot module for having some fun with people.
import asyncio
import random
import re

import requests
from cowpy import cow
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChannelParticipantsAdmins, MessageEntityMentionName

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers import catmemes
from ..helpers.utils import _catutils, parse_pre
from . import BOTLOG, BOTLOG_CHATID, mention

plugin_category = "fun"


async def get_user(event):
    # Get the user from argument or replied message
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await event.client(
            GetFullUserRequest(previous_message.sender_id)
        )
    else:
        user = event.pattern_match.group(1)
        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await event.client.get_me()
            user = self_user.id

        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(GetFullUserRequest(user_object.id))

        except (TypeError, ValueError):
            await event.edit("`I don't slap aliens , they are ugly af`")
            return None
    return replied_user


@catub.cat_cmd(
    pattern="(\w+)say ([\s\S]*)",
    command=("cowsay", plugin_category),
    info={
        "header": "A fun art plugin",
        "types": [
            "default",
            "beavis",
            "bongcow",
            "budfrogs",
            "bunny",
            "cheese",
            "cower",
            "daemon",
            "dragonandcow",
            "eyes",
            "flamingsheep",
            "ghostbusters",
            "headincow",
            "hellokitty",
            "kiss",
            "kitty",
            "koala",
            "kosh",
            "lukekoala",
            "mechandcow",
            "meow",
            "milk",
            "moofasa",
            "moose",
            "mutilated",
            "ren",
            "satanic",
            "sheep",
            "skeleton",
            "small",
            "sodomized",
            "squirrel",
            "stegosaurus",
            "stimpy",
            "supermilker",
            "surgery",
            "telebears",
            "threeeyes",
            "turkey",
            "turtle",
            "tux",
            "udder",
            "vaderkoala",
            "vader",
            "www",
        ],
        "usage": [
            "{tr}cowsay <text>",
            "{tr}<type>say <text>",
        ],
        "examples": [
            "{tr}squirrelsay Catuserbot",
            "{tr}milksay catuserbot",
            "{tr}ghostbustersghostbusterssay Catuserbot",
        ],
    },
)
async def univsaye(cowmsg):
    "A fun art plugin"
    arg = cowmsg.pattern_match.group(1).lower()
    text = cowmsg.pattern_match.group(2)
    if arg == "cow":
        arg = "default"
    if arg not in cow.COWACTERS:
        return await edit_delete(cowmsg, "Check help menu to know the correct options")
    cheese = cow.get_cow(arg)
    cheese = cheese()
    await edit_or_reply(cowmsg, f"`{cheese.milk(text).replace('`', '´')}`")


@catub.cat_cmd(
    pattern="coin ?([\s\S]*)",
    command=("coin", plugin_category),
    info={
        "header": "Coin flipper",
        "usage": [
            "{tr}coin <heads/tails>",
            "{tr}coin",
        ],
    },
)
async def _(event):
    "Flips a coin"
    r = random.randint(1, 100)
    input_str = event.pattern_match.group(1)
    if input_str:
        input_str = input_str.lower()
    if r % 2 == 1:
        if input_str == "heads":
            await edit_or_reply(
                event, "The coin landed on : **Heads**\n\nYou were correct"
            )
        elif input_str == "tails":
            await edit_or_reply(
                event,
                "The coin landed on : **Heads**\n\nYou weren't correct , try again...",
            )
        else:
            await edit_or_reply(event, "The coin landed on : **Heads**")
    elif r % 2 == 0:
        if input_str == "tails":
            await edit_or_reply(
                event, "The coin landed on : **Tails**\n\nYou were correct"
            )
        elif input_str == "heads":
            await edit_or_reply(
                event,
                "The coin landed on : **Tails**\n\nYou weren't correct , try again...",
            )
        else:
            await edit_or_reply(event, "The coin landed on : **Tails**")
    else:
        await edit_or_reply(event, r"¯\_(ツ)_/¯")


@catub.cat_cmd(
    pattern="slap(?:\s|$)([\s\S]*)",
    command=("slap", plugin_category),
    info={
        "header": "To slap a person with random objects",
        "usage": "{tr}slap reply/username>",
    },
)
async def who(event):
    "To slap a person with random objects"
    replied_user = await get_user(event)
    if replied_user is None:
        return
    caption = await catmemes.slap(replied_user, event, mention)
    try:
        await edit_or_reply(event, caption)
    except BaseException:
        await edit_or_reply(
            event, "`Can't slap this person , need to fetch some sticks and stones`"
        )


@catub.cat_cmd(
    pattern="(yes|no|maybe|decide)$",
    command=("decide", plugin_category),
    info={
        "header": "To decide something will send gif according to given input or ouput",
        "usage": [
            "{tr}yes",
            "{tr}no",
            "{tr}maybe",
            "{tr}decide",
        ],
    },
)
async def decide(event):
    "To send random gif associated with yes or no or maybe"
    decision = event.pattern_match.group(1).lower()
    message_id = event.reply_to_msg_id or None
    if decision != "decide":
        r = requests.get(f"https://yesno.wtf/api?force={decision}").json()
    else:
        r = requests.get("https://yesno.wtf/api").json()
    await event.delete()
    sandy = await event.client.send_message(
        event.chat_id, str(r["answer"]).upper(), reply_to=message_id, file=r["image"]
    )
    await _catutils.unsavegif(event, sandy)


@catub.cat_cmd(
    pattern="shout(?:\s|$)([\s\S]*)",
    command=("shout", plugin_category),
    info={
        "header": "Shouts the text in a fun way",
        "usage": [
            "{tr}shout <text>",
        ],
    },
)
async def shout(args):
    "Shouts the text in a fun way"
    input_str = args.pattern_match.group(1)
    if not input_str:
        return await edit_delete(args, "What should I shout ?")
    words = input_str.split()
    msg = ""
    for messagestr in words:
        text = " ".join(messagestr)
        result = [" ".join(text)]
        for pos, symbol in enumerate(text[1:]):
            result.append(symbol + " " + "  " * pos + symbol)
        result = list("\n".join(result))
        result[0] = text[0]
        result = "".join(result)
        msg += "\n" + result
        if len(words) > 1:
            msg += "\n\n----------\n"
    await edit_or_reply(args, msg, parse_mode=parse_pre)


@catub.cat_cmd(
    pattern="owo ?([\s\S]*)",
    command=("owo", plugin_category),
    info={
        "header": "Check yourself",
        "usage": [
            "{tr}owo <text>",
        ],
    },
)
async def faces(owo):
    "UwU"
    textx = await owo.get_reply_message()
    message = owo.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        return await edit_or_reply(owo, "`No text given`")
    reply_text = re.sub(r"(r|l)", "w", message)
    reply_text = re.sub(r"(R|L)", "W", reply_text)
    reply_text = re.sub(r"n([aeiou])", r"ny\1", reply_text)
    reply_text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
    reply_text = re.sub(r"\!+", " " + random.choice(catmemes.UWUS), reply_text)
    reply_text = reply_text.replace("ove", "uv")
    reply_text += " " + random.choice(catmemes.UWUS)
    await edit_or_reply(owo, reply_text)


@catub.cat_cmd(
    pattern="clap(?:\s|$)([\s\S]*)",
    command=("clap", plugin_category),
    info={
        "header": "Praise people",
        "usage": [
            "{tr}clap <text>",
        ],
    },
)
async def claptext(event):
    "Praise people"
    textx = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif textx.message:
        query = textx.message
    else:
        return await edit_or_reply(event, "`Ha ha I don't clap pointlessly !`")
    reply_text = "👏🏻 "
    reply_text += query.replace(" ", " 👏🏻 ")
    reply_text += " 👏🏻"
    await edit_or_reply(event, reply_text)


@catub.cat_cmd(
    pattern="smk(?:\s|$)([\s\S]*)",
    command=("smk", plugin_category),
    info={
        "header": "A shit module for ツ , who cares",
        "usage": [
            "{tr}smk <text>",
        ],
    },
)
async def smrk(smk):
    "A shit module for ツ , who cares"
    textx = await smk.get_reply_message()
    if smk.pattern_match.group(1):
        message = smk.pattern_match.group(1)
    elif textx.message:
        message = textx.message
    else:
        await edit_or_reply(smk, "ツ")
        return
    if message == "Dele":
        await edit_or_reply(smk, message + "Te the hell" + "ツ")
    else:
        smirk = " ツ"
        reply_text = message + smirk
        await edit_or_reply(smk, reply_text)


@catub.cat_cmd(
    pattern="f ([\s\S]*)",
    command=("f", plugin_category),
    info={
        "header": "Pay respects",
        "usage": [
            "{tr}f <emoji/character>",
        ],
    },
)
async def payf(event):
    "Pay respects"
    paytext = event.pattern_match.group(1)
    pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        paytext * 8,
        paytext * 8,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 6,
        paytext * 6,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 2,
        paytext * 2,
    )
    await edit_or_reply(event, pay)

    
@catub.cat_cmd(
    pattern="lfy(?:\s|$)([\s\S]*)",
    command=("lfy", plugin_category),
    info={
        "header": "Let me google that for you real quick",
        "usage": [
            "{tr}lfy <query>",
        ],
    },
)
async def _(event):
    "Let me google that for you real quick"
    input_str = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not input_str and reply:
        input_str = reply.text
    if not input_str:
        return await edit_delete(
            event, "`Either reply to text message or give input to search`", 5
        )
    sample_url = f"https://da.gd/s?url=https://lmgtfy.com/?q={input_str.replace(' ', '+')}%26iie=1"
    response_api = requests.get(sample_url).text
    if response_api:
        await edit_or_reply(
            event, f"[{input_str}]({response_api.rstrip()})\n\n`Thank me later 🙃` "
        )
    else:
        return await edit_delete(
            event, "`Something is wrong please try again later`", 5
        )
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"Let me google that for you query `{input_str}` was executed successfully",
        )


@catub.cat_cmd(
    pattern="gbun(?:\s|$)([\s\S]*)",
    command=("gbun", plugin_category),
    info={
        "header": "Fake gban action",
        "usage": ["{tr}gbun <reason>", "{tr}gbun"],
    },
)
async def gbun(event):
    "Fake gban action"
    gbunVar = event.text
    gbunVar = gbunVar[6:]
    mentions = "`Warning\n\nUser gbanned by admin...\n`"
    catevent = await edit_or_reply(event, "Summoning out le gungnir ☠️")
    await asyncio.sleep(3.5)
    chat = await event.get_input_chat()
    async for _ in event.client.iter_participants(
        chat, filter=ChannelParticipantsAdmins
    ):
        mentions += f""
    reply_message = None
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        replied_user = await event.client(GetFullUserRequest(reply_message.sender_id))
        firstname = replied_user.user.first_name
        usname = replied_user.user.username
        idd = reply_message.sender_id
        # make meself invulnerable cuz why not xD
        if idd == 1035034432:
            await catevent.edit(
                "`Wait a second , this is my mistress`\n\nHow dare you threaten to ban my mistress ?\n\nYour account has been hacked ! Pay 1000$ to my mistress [π.$](tg://user?id=1035034432) to release your account 😏"
            )
        else:
            jnl = (
                "`Warning`"
                "[{}](tg://user?id={})"
                "`gbanned by admin...\n\n`"
                "**User's name : ** {}\n"
                "**Id : ** `{}`\n"
            ).format(firstname, idd, firstname, idd)
            if usname is None:
                jnl += "**Victim nigga's username : ** `Doesn't own a username`\n"
            else:
                jnl += "**Victim nigga's username** : @{}\n".format(usname)
            if len(gbunVar) > 0:
                gbunm = "`{}`".format(gbunVar)
                gbunr = "**Reason :**" + gbunm
                jnl += gbunr
            else:
                no_reason = "Reason : Potential spammer"
                jnl += no_reason
            await catevent.edit(jnl)
    else:
        mention = "`Warning\n\nUser gbanned by admin...\n\nReason : Potential spammer `"
        await catevent.edit(mention)
