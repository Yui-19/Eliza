# ======================================================================================================================================

# By @Yui
import os
from datetime import datetime

from userbot import catub

from . import hmention, reply_id

"""
try:
    from . import PING_PIC, PING_TEXT
except:
    pass
"""

plugin_category = "extra"

PING_PIC = os.environ.get("PING_PIC")  # or Config.PING_PIC

PING_TEXT = (
    os.environ.get("CUSTOM_PING_TEXT", None)
    or "<i>Be fast or be last</i>"
)


@catub.cat_cmd(
    pattern="pping$",
    command=("pping", plugin_category),
    info={
        "header": "Check how long it takes to ping your userbot",
        "option": "To show media in this cmd you need to set PING_PIC with media link get this by replying the media by .tgm",
        "usage": [
            "{tr}pping",
        ],
    },
)
async def _(event):

    if event.fwd_from:

        return

    reply_to_id = await reply_id(event)

    start = datetime.now()

    cat = await edit_or_reply(event, "<i>Pong</i>", "html")

    end = datetime.now()
   

    ms = (end - start).microseconds/1000

    if PING_PIC:

        caption = f"<i>{PING_TEXT}<i>\n\n<i>➤ Pong</i>\n{ms} <i>ms</i>\n<i>➤ Boss : {hmention}</i>"

        await event.client.send_file(
            event.chat_id,
            PING_PIC,
            caption=caption,
            parse_mode="html",
            reply_to=reply_to_id,
            link_preview=False,
            allow_cache=True,
        )

    else:

        await edit_or_reply(event, "<code>Add PING_PIC first<code>", "html")


# ======================================================================================================================================
