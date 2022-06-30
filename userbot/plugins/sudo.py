from datetime import datetime

from telethon.utils import get_display_name

from userbot import catub
from userbot.core.logger import logging

from ..Config import Config
from ..core import CMD_INFO, PLG_INFO
from ..core.data import _sudousers_list, sudo_enabled_cmds
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import get_user_from_event, mentionuser
from ..sql_helper import global_collectionjson as sql
from ..sql_helper import global_list as sqllist
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "tools"

LOGS = logging.getLogger(__name__)


async def _init() -> None:
    sudousers = _sudousers_list()
    Config.SUDO_USERS.clear()
    for user_d in sudousers:
        Config.SUDO_USERS.add(user_d)


def get_key(val):
    for key, value in PLG_INFO.items():
        for cmd in value:
            if val == cmd:
                return key
    return None


@catub.cat_cmd(
    pattern="sudo (on|off)$",
    command=("sudo", plugin_category),
    info={
        "header": "To enable or disable sudo of your catuserbot",
        "description": "Initially all sudo commands are disabled you need to enable them by addscmd\n\nCheck `{tr}help -c addscmd`",
        "usage": "{tr}sudo <on/off>",
    },
)
async def chat_blacklist(event):
    "To enable or disable sudo of your cat userbot"
    input_str = event.pattern_match.group(1)
    sudousers = _sudousers_list()
    if input_str == "on":
        if gvarstatus("sudoenable") is not None:
            return await edit_delete(event, "Sudo is already enabled")
        addgvar("sudoenable", "true")
        text = "Enabled sudo successfully\n"
        if len(sudousers) != 0:
            text += (
                "Bot is reloading to apply the changes please wait for a minute"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        text += "You haven't added anyone to your sudo yet"
        return await edit_or_reply(
            event,
            text,
        )
    if gvarstatus("sudoenable") is not None:
        delgvar("sudoenable")
        text = "Disabled sudo successfully"
        if len(sudousers) != 0:
            text += (
                "Bot is reloading to apply the changes please wait for a minute"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        text += "You haven't added any chat to blacklist yet"
        return await edit_or_reply(
            event,
            text,
        )
    await edit_delete(event, "It was turned off already")


@catub.cat_cmd(
    pattern="addsudo(?:\s|$)([\s\S]*)",
    command=("addsudo", plugin_category),
    info={
        "header": "To add user as your sudo",
        "usage": "{tr}addsudo <username/reply/mention>",
    },
)
async def add_sudo_user(event):
    "To add user to sudo"
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    if replied_user.id == event.client.uid:
        return await edit_delete(event, "You can't add yourself to sudo")
    if replied_user.id in _sudousers_list():
        return await edit_delete(
            event,
            f"{mentionuser(get_display_name(replied_user),replied_user.id)} is already in your sudo list",
        )
    date = str(datetime.now().strftime("%B %d, %Y"))
    userdata = {
        "chat_id": replied_user.id,
        "chat_name": get_display_name(replied_user),
        "chat_username": replied_user.username,
        "date": date,
    }
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    sudousers[str(replied_user.id)] = userdata
    sql.del_collection("sudousers_list")
    sql.add_collection("sudousers_list", sudousers, {})
    output = f"{mentionuser(userdata['chat_name'],userdata['chat_id'])} is added to your sudo users\n\n"
    output += "**Bot is reloading to apply the changes please wait for a minute**"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="delsudo(?:\s|$)([\s\S]*)",
    command=("delsudo", plugin_category),
    info={
        "header": "To remove user from your sudo",
        "usage": "{tr}delsudo <username/reply/mention>",
    },
)
async def _(event):
    "To del user from sudo."
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    if str(replied_user.id) not in sudousers:
        return await edit_delete(
            event,
            f"{mentionuser(get_display_name(replied_user),replied_user.id)} is not in your sudo",
        )
    del sudousers[str(replied_user.id)]
    sql.del_collection("sudousers_list")
    sql.add_collection("sudousers_list", sudousers, {})
    output = f"{mentionuser(get_display_name(replied_user),replied_user.id)} is removed from your sudo users\n\n"
    output += "Bot is reloading to apply the changes please wait for a minute"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="vsudo$",
    command=("vsudo", plugin_category),
    info={
        "header": "To list users for whom you are sudo",
        "usage": "{tr}vsudo",
    },
)
async def _(event):
    "To list Your sudo users"
    sudochats = _sudousers_list()
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    if len(sudochats) == 0:
        return await edit_delete(
            event, "There are no sudo users for your cat userbot"
        )
    result = "The list of sudo users for your cat userbot are :\n\n"
    for chat in sudochats:
        result += f"Name: {mentionuser(sudousers[str(chat)]['chat_name'],sudousers[str(chat)]['chat_id'])}\n\n"
        result += f"Chat id : `{chat}`\n\n"
        username = f"@{sudousers[str(chat)]['chat_username']}" or "None"
        result += f"Username : {username}\n\n"
        result += f"Added on {sudousers[str(chat)]['date']}\n\n"
    await edit_or_reply(event, result)


@catub.cat_cmd(
    pattern="addscmd(s)?(?:\s|$)([\s\S]*)",
    command=("addscmd", plugin_category),
    info={
        "header": "To enable cmds for sudo users",
        "flags": {
            "-all": "Will enable all commands for sudo users ( except few like eval , exec , profile )",
            "-full": "Will add all commands including eval , exec etc compelete sudo",
            "-p": "Will add all commands from the given plugin names",
        },
        "usage": [
            "{tr}addscmd -all",
            "{tr}addscmd -full",
            "{tr}addscmd -p <plugin names>",
            "{tr}addscmd <commands>",
        ],
        "examples": [
            "{tr}addscmd -p autoprofile botcontrols i.e, for multiple names use space between each name",
            "{tr}addscmd ping alive i.e, for multiple names use space between each name",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To enable commands for sudo users"
    input_str = event.pattern_match.group(2)
    errors = ""
    sudocmds = sudo_enabled_cmds()
    if not input_str:
        return await edit_or_reply(
            event, "Which command should I enable for sudo users"
        )
    input_str = input_str.split()
    if input_str[0] == "-all":
        catevent = await edit_or_reply(event, "Enabling all safe commands for sudo...")
        totalcmds = CMD_INFO.keys()
        flagcmds = (
            PLG_INFO["botcontrols"]
            + PLG_INFO["autoprofile"]
            + PLG_INFO["evaluators"]
            + PLG_INFO["execmod"]
            + PLG_INFO["heroku"]
            + PLG_INFO["profile"]
            + PLG_INFO["pmpermit"]
            + PLG_INFO["custom"]
            + PLG_INFO["blacklistchats"]
            + PLG_INFO["corecmds"]
            + PLG_INFO["groupactions"]
            + PLG_INFO["sudo"]
            + PLG_INFO["transfer_channel"]
            + ["gauth"]
            + ["greset"]
        )
        loadcmds = list(set(totalcmds) - set(flagcmds))
        if len(sudocmds) > 0:
            sqllist.del_keyword_list("sudo_enabled_cmds")
    elif input_str[0] == "-full":
        catevent = await edit_or_reply(
            event, "Enabling compelete sudo for users..."
        )
        loadcmds = CMD_INFO.keys()
        if len(sudocmds) > 0:
            sqllist.del_keyword_list("sudo_enabled_cmds")
    elif input_str[0] == "-p":
        catevent = event
        input_str.remove("-p")
        loadcmds = []
        for plugin in input_str:
            if plugin not in PLG_INFO:
                errors += (
                    f"`{plugin}` There is no such plugin in your cat userbot\n"
                )
            else:
                loadcmds += PLG_INFO[plugin]
    else:
        catevent = event
        loadcmds = []
        for cmd in input_str:
            if cmd not in CMD_INFO:
                errors += f"`{cmd}` There is no such command in your cat userbot\n"
            elif cmd in sudocmds:
                errors += f"`{cmd}` is already enabled for sudo users\n"
            else:
                loadcmds.append(cmd)
    for cmd in loadcmds:
        sqllist.add_to_list("sudo_enabled_cmds", cmd)
    result = f"Successfully enabled `{len(loadcmds)}` for cat userbot sudo\n"
    output = (
        result + "Bot is reloading to apply the changes please wait for a minute\n"
    )
    if errors != "":
        output += "\nErrors :\n" + errors
    msg = await edit_or_reply(catevent, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="rmscmd(s)?(?:\s|$)([\s\S]*)?",
    command=("rmscmd", plugin_category),
    info={
        "header": "To disable given cmds for sudo",
        "flags": {
            "-all": "Will disable all enabled cmds for sudo users",
            "-flag": "Will disable all flaged cmds like eval , exec etc",
            "-p": "Will disable all cmds from the given plugin names",
        },
        "usage": [
            "{tr}rmscmd -all",
            "{tr}rmscmd -flag",
            "{tr}rmscmd -p <plugin names>",
            "{tr}rmscmd <commands>",
        ],
        "examples": [
            "{tr}rmscmd -p autoprofile botcontrols i.e. for multiple names use space between each name",
            "{tr}rmscmd ping alive i.e, for multiple commands use space between each name",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To disable cmds for sudo users"
    input_str = event.pattern_match.group(2)
    errors = ""
    sudocmds = sudo_enabled_cmds()
    if not input_str:
        return await edit_or_reply(
            event, "Which command should I disable for sudo users ?"
        )
    input_str = input_str.split()
    if input_str[0] == "-all":
        catevent = await edit_or_reply(
            event, "Disabling all enabled commands for sudo..."
        )
        flagcmds = sudocmds
    elif input_str[0] == "-flag":
        catevent = await edit_or_reply(
            event, "Disabling all flagged commands for sudo..."
        )
        flagcmds = (
            PLG_INFO["botcontrols"]
            + PLG_INFO["autoprofile"]
            + PLG_INFO["evaluators"]
            + PLG_INFO["execmod"]
            + PLG_INFO["heroku"]
            + PLG_INFO["profile"]
            + PLG_INFO["pmpermit"]
            + PLG_INFO["custom"]
            + PLG_INFO["blacklistchats"]
            + PLG_INFO["corecmds"]
            + PLG_INFO["groupactions"]
            + PLG_INFO["sudo"]
            + PLG_INFO["transfer_channel"]
            + ["gauth"]
            + ["greset"]
        )
    elif input_str[0] == "-p":
        catevent = event
        input_str.remove("-p")
        flagcmds = []
        for plugin in input_str:
            if plugin not in PLG_INFO:
                errors += (
                    f"`{plugin}` There is no such plugin in your cat userbot\n"
                )
            else:
                flagcmds += PLG_INFO[plugin]
    else:
        catevent = event
        flagcmds = []
        for cmd in input_str:
            if cmd not in CMD_INFO:
                errors += f"`{cmd}` There is no such command in your cat userbot\n"
            elif cmd not in sudocmds:
                errors += f"`{cmd}` is already disabled for sudo users\n"
            else:
                flagcmds.append(cmd)
    count = 0
    for cmd in flagcmds:
        if sqllist.is_in_list("sudo_enabled_cmds", cmd):
            count += 1
            sqllist.rm_from_list("sudo_enabled_cmds", cmd)
    result = f"Successfully disabled `{count}` for cat userbot sudo\n"
    output = (
        result + "Bot is reloading to apply the changes please wait for a minute\n"
    )
    if errors != "":
        output += "\nErrors :\n" + errors
    msg = await edit_or_reply(catevent, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="vscmds( -d)?$",
    command=("vscmds", plugin_category),
    info={
        "header": "To show list of enabled commands for sudo",
        "description": "Will show you the list of all enabled commands",
        "flags": {"-d": "To show disabled commands instead of enabled commands"},
        "usage": [
            "{tr}vscmds",
            "{tr}vscmds -d",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To show list of enabled commands for sudo"
    input_str = event.pattern_match.group(1)
    sudocmds = sudo_enabled_cmds()
    clist = {}
    error = ""
    if not input_str:
        text = "The list of sudo enabled commands are :"
        result = "SUDO ENABLED COMMANDS"
        if len(sudocmds) > 0:
            for cmd in sudocmds:
                plugin = get_key(cmd)
                if plugin in clist:
                    clist[plugin].append(cmd)
                else:
                    clist[plugin] = [cmd]
        else:
            error += "You haven't enabled any sudo cmd for sudo users"
        count = len(sudocmds)
    else:
        text = "The list of sudo disabled commands are :"
        result = "SUDO DISABLED COMMANDS"
        totalcmds = CMD_INFO.keys()
        cmdlist = list(set(totalcmds) - set(sudocmds))
        if cmdlist:
            for cmd in cmdlist:
                plugin = get_key(cmd)
                if plugin in clist:
                    clist[plugin].append(cmd)
                else:
                    clist[plugin] = [cmd]
        else:
            error += "You have enabled every command as sudo for sudo users"
        count = len(cmdlist)
    if error != "":
        return await edit_delete(event, error, 10)
    pkeys = clist.keys()
    n_pkeys = [i for i in pkeys if i is not None]
    pkeys = sorted(n_pkeys)
    output = ""
    for plugin in pkeys:
        output += f"• {plugin}\n"
        for cmd in clist[plugin]:
            output += f"`{cmd}` "
        output += "\n\n"
    finalstr = (
        result
        + f"\n\nSUDO TRIGGER : `{Config.SUDO_COMMAND_HAND_LER}`\n\nCommands : {count}\n\n"
        + output
    )
    await edit_or_reply(event, finalstr, aslink=True, linktext=text)


catub.loop.create_task(_init())
