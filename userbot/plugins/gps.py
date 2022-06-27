from geopy.geocoders import Nominatim
from telethon.tl import types

from userbot import catub

from ..core.managers import edit_or_reply
from ..helpers import reply_id

plugin_category = "extra"


@catub.cat_cmd(
    pattern="gps ([\s\S]*)",
    command=("gps", plugin_category),
    info={
        "header": "To send the map of the given location",
        "usage": "{tr}gps <place>",
        "examples": "{tr}gps hyderabad",
    },
)
async def gps(event):
    "Map of the given location"
    reply_to_id = await reply_id(event)
    input_str = event.pattern_match.group(1)
    catevent = await edit_or_reply(event, "`Finding...`")
    geolocator = Nominatim(user_agent="catuserbot")
    geoloc = geolocator.geocode(input_str)
    if geoloc:
        lon = geoloc.longitude
        lat = geoloc.latitude
        await event.client.send_file(
            event.chat_id,
            file=types.InputMediaGeoPoint(types.InputGeoPoint(lat, lon)),
            caption=f"**Location : **`{input_str}`",
            reply_to=reply_to_id,
        )
        await catevent.delete()
    else:
        await catevent.edit("`I coudn't find it`")
