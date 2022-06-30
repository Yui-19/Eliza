import os
from datetime import datetime

import aiohttp
import requests
from github import Github
from pySmartDL import SmartDL

from userbot import catub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id
from . import reply_id

LOGS = logging.getLogger(os.path.basename(__name__))
ppath = os.path.join(os.getcwd(), "temp", "githubuser.jpg")
plugin_category = "misc"

GIT_TEMP_DIR = "./temp/"


@catub.cat_cmd(
    pattern="repo$",
    command=("repo", plugin_category),
    info={
        "header": "Source code link of userbot",
        "usage": [
            "{tr}repo",
        ],
    },
)
async def source(e):
    "Source code link of userbot"
    await edit_or_reply(
        e,
        "Click [here](https://github.com/Yui-19/Eliza) to open this bot source code\
        \n\nClick [here](https://github.com/Yui-19/Eliza) to open supported link for heroku",
    )


@catub.cat_cmd(
    pattern="github( -l(\d+))? ([\s\S]*)",
    command=("github", plugin_category),
    info={
        "header": "Shows the information about an user on github of given username",
        "flags": {"-l": "repo limit : default to 5"},
        "usage": ".github [flag] [username]",
        "examples": [".github sandy1709", ".github -l5 sandy1709"],
    },
)
async def _(event):
    "Get info about an github user"
    reply_to = await reply_id(event)
    username = event.pattern_match.group(3)
    URL = f"https://api.github.com/users/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                return await edit_delete(event, f"`{username} not found`")
            catevent = await edit_or_reply(event, "`Fetching github info...`")
            result = await request.json()
            photo = result["avatar_url"]
            if result["bio"]:
                result["bio"] = result["bio"].strip()
            repos = []
            sec_res = requests.get(result["repos_url"])
            if sec_res.status_code == 200:
                limit = event.pattern_match.group(2)
                limit = 5 if not limit else int(limit)
                for repo in sec_res.json():
                    repos.append(f"[{repo['name']}]({repo['html_url']})")
                    limit -= 1
                    if limit == 0:
                        break
            REPLY = "Github info for `{username}`\
                \n\nName : [{name}]({html_url})\
                \n\nType : `{type}`\
                \n\nCompany : `{company}`\
                \n\nBlog : {blog}\
                \n\nLocation : `{location}`\
                \n\nBio : __{bio}__\
                \n\nFollowers : `{followers}`\
                \n\nFollowing : `{following}`\
                \n\nPublic repos : `{public_repos}`\
                \n\nPublic gists : `{public_gists}`\
                \n\nProfile created : `{created_at}`\
                \n\nProfile updated : `{updated_at}`".format(
                username=username, **result
            )

            if repos:
                REPLY += "\n👀 Some repos : " + " | ".join(repos)
            downloader = SmartDL(photo, ppath, progress_bar=False)
            downloader.start(blocking=False)
            while not downloader.isFinished():
                pass
            await event.client.send_file(
                event.chat_id,
                ppath,
                caption=REPLY,
                reply_to=reply_to,
            )
            os.remove(ppath)
            await catevent.delete()


@catub.cat_cmd(
    pattern="commit$",
    command=("commit", plugin_category),
    info={
        "header": "To commit the replied plugin to github",
        "description": "It uploads the given file to your github repo in **userbot or plugins** folder\
        \n\nTo work commit plugin set `GITHUB_ACCESS_TOKEN` and `GIT_REPO_NAME` variables in heroku vars first",
        "note": "As of now not needed i will sure develop it ",
        "usage": "{tr}commit",
    },
)
async def download(event):
    "To commit the replied plugin to github"
    if Config.GITHUB_ACCESS_TOKEN is None:
        return await edit_delete(
            event, "`Please add proper access token from github.com`", 5
        )
    if Config.GIT_REPO_NAME is None:
        return await edit_delete(
            event, "`Please add proper github repo name of your userbot`", 5
        )
    mone = await edit_or_reply(event, "`Processing...`")
    if not os.path.isdir(GIT_TEMP_DIR):
        os.makedirs(GIT_TEMP_DIR)
    start = datetime.now()
    reply_message = await event.get_reply_message()
    if not reply_message or not reply_message.media:
        return await edit_delete(
            event, "Reply to a file which you want to commit in your github"
        )
    try:
        downloaded_file_name = await event.client.download_media(reply_message.media)
    except Exception as e:
        await mone.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await mone.edit(
            "Downloaded to `{}` in {} seconds".format(downloaded_file_name, ms)
        )
        await mone.edit("Committing to github...")
        await git_commit(downloaded_file_name, mone)


async def git_commit(file_name, mone):
    content_list = []
    access_token = Config.GITHUB_ACCESS_TOKEN
    g = Github(access_token)
    file = open(file_name, "r", encoding="utf-8")
    commit_data = file.read()
    repo = g.get_repo(Config.GIT_REPO_NAME)
    LOGS.info(repo.name)
    create_file = True
    contents = repo.get_contents("")
    for content_file in contents:
        content_list.append(str(content_file))
        LOGS.info(content_file)
    for i in content_list:
        create_file = True
        if i == 'ContentFile(path="' + file_name + '")':
            return await mone.edit("`File already exists`")
    if create_file:
        file_name = f"userbot/plugins/{file_name}"
        LOGS.info(file_name)
        try:
            repo.create_file(
                file_name, "Uploaded new plugin", commit_data, branch="master"
            )
            LOGS.info("Committed file")
            ccess = Config.GIT_REPO_NAME
            ccess = ccess.strip()
            await mone.edit(
                f"`Commited on your github repo`\n\n[Your plugins](https://github.com/{ccess}/tree/master/userbot/plugins/)"
            )
        except BaseException:
            LOGS.info("Cannot create plugin")
            await mone.edit("Cannot upload plugin")
    else:
        return await mone.edit("`Committed suicide`")
