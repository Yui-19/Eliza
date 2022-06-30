# corona virus stats for catuserbot
from covid import Covid

from . import catub, covidindia, edit_delete, edit_or_reply

plugin_category = "extra"


@catub.cat_cmd(
    pattern="covid(?:\s|$)([\s\S]*)",
    command=("covid", plugin_category),
    info={
        "header": "To get latest information about covid-19",
        "description": "Get information about covid-19 data in the given country or state ( only indian states )",
        "usage": "{tr}covid <state_name/country_name>",
        "examples": ["{tr}covid andhra pradesh", "{tr}covid india", "{tr}covid world"],
    },
)
async def corona(event):
    "To get latest information about covid-19"
    input_str = event.pattern_match.group(1)
    country = (input_str).title() if input_str else "World"
    catevent = await edit_or_reply(event, "`Collecting data`")
    covid = Covid(source="worldometers")
    try:
        country_data = covid.get_status_by_country_name(country)
    except ValueError:
        country_data = ""
    if country_data:
        hmm1 = country_data["confirmed"] + country_data["new_cases"]
        hmm2 = country_data["deaths"] + country_data["new_deaths"]
        data = ""
        data += f"\n\nConfirmed : <code>{hmm1}</code>"
        data += f"\n\nActive : <code>{country_data['active']}</code>"
        data += f"\n\nDeaths : <code>{hmm2}</code>"
        data += f"\n\nCritical : <code>{country_data['critical']}</code>"
        data += f"\n\nRecovered : <code>{country_data['recovered']}</code>"
        data += f"\n\nTotal tests : <code>{country_data['total_tests']}</code>"
        data += f"\n\nNew cases : <code>{country_data['new_cases']}</code>"
        data += f"\n\nNew deaths : <code>{country_data['new_deaths']}</code>"
        await catevent.edit(
            "<b>Corona virus info of {}:\n{}</b>".format(country, data),
            parse_mode="html",
        )
    else:
        data = await covidindia(country)
        if data:
            cat1 = int(data["new_positive"]) - int(data["positive"])
            cat2 = int(data["new_death"]) - int(data["death"])
            cat3 = int(data["new_cured"]) - int(data["cured"])
            result = f"<b>Corona virus info of {data['state_name']}\
                \n\nConfirmed : <code>{data['new_positive']}</code>\
                \n\nActive : <code>{data['new_active']}</code>\
                \n\nDeaths : <code>{data['new_death']}</code>\
                \n\nRecovered : <code>{data['new_cured']}</code>\
                \n\nNew cases : <code>{cat1}</code>\
                \n\nNew deaths : <code>{cat2}</code>\
                \n\nNew cured : <code>{cat3}</code> </b>"
            await catevent.edit(result, parse_mode="html")
        else:
            await edit_delete(
                catevent,
                "`Corona virus info of {} is not available or unable to fetch`".format(
                    country
                ),
                5,
            )
