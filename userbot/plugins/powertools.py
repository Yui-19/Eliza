import os
from asyncio.exceptions import CancelledError
from time import sleep

from userbot import catub

from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..sql_helper.global_collection import (
    add_to_collectionlist,
    del_keyword_collectionlist,
    get_collectionlist_items,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID, HEROKU_APP

LOGS = logging.getLogger(__name__)
plugin_category = "tools"


@catub.cat_cmd(
    pattern="restart$",
    command=("restart", plugin_category),
    info={
        "header": "Restarts the bot",
        "usage": "{tr}restart",
    },
    disable_errors=True,
)
async def _(event):
    "Restarts the bot"
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "RESTART\nBot restarted")
    sandy = await edit_or_reply(
        event,
        "Restarted\n\n`.ping` me or `.help` to check if I am online actually it takes 1-2 minutes for restarting",
    )
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [sandy.chat_id, sandy.id])
    except Exception as e:
        LOGS.error(e)
    try:
        await catub.disconnect()
    except CancelledError:
        pass
    except Exception as e:
        LOGS.error(e)


@catub.cat_cmd(
    pattern="shutdown$",
    command=("shutdown", plugin_category),
    info={
        "header": "Shutdowns the bot",
        "description": "To turn off the dyno of heroku you can't turn on by bot you need to got to heroku and turn on or use @hk_heroku_bot",
        "usage": "{tr}shutdown",
    },
)
async def _(event):
    "Shutdowns the bot"
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "SHUT DOWN\n\nBot shut down")
    await edit_or_reply(event, "`Turning off bot now... Manually turn me on later`")
    if HEROKU_APP is not None:
        HEROKU_APP.process_formation()["worker"].scale(0)
    else:
        os._exit(143)


@catub.cat_cmd(
    pattern="sleep( [0-9]+)?$",
    command=("sleep", plugin_category),
    info={
        "header": "Userbot will stop working for the mentioned time",
        "usage": "{tr}sleep <seconds>",
        "examples": "{tr}sleep 60",
    },
)
async def _(event):
    "To sleep the userbot"
    if " " not in event.pattern_match.group(1):
        return await edit_or_reply(event, "Syntax: `.sleep time`")
    counter = int(event.pattern_match.group(1))
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "You put the bot to sleep for " + str(counter) + " seconds",
        )
    event = await edit_or_reply(event, f"`Okay let me sleep for {counter} seconds`")
    sleep(counter)
    await event.edit("`Okay I'm awake now`")


@catub.cat_cmd(
    pattern="notify (on|off)$",
    command=("notify", plugin_category),
    info={
        "header": "To update the your chat after restart or reload",
        "description": "Will send the ping cmd as reply to the previous last message of ( restart or reload or update commands )",
        "usage": [
            "{tr}notify <on/off>",
        ],
    },
)
async def set_pmlog(event):
    "To update the your chat after restart or reload"
    input_str = event.pattern_match.group(1)
    if input_str == "off":
        if gvarstatus("restartupdate") is None:
            return await edit_delete(event, "Notify was already disabled")
        delgvar("restartupdate")
        return await edit_or_reply(event, "Notify was disabled successfully")
    if gvarstatus("restartupdate") is None:
        addgvar("restartupdate", "turn-oned")
        return await edit_or_reply(event, "Notify was enabled successfully")
    await edit_delete(event, "Notify was already enabled")
