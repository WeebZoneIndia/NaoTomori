import re
import html

from texas.decorator import register
from texas.services.mongo import db
from .utils.disable import disableable_dec
from .utils.language import get_strings_dec
from .utils.message import get_args_str
from .utils.user_details import get_user_link, get_user, get_user_by_id


@register(cmds="afk")
@disableable_dec("afk")
@get_strings_dec("afk")
async def afk(message, strings):
    arg = get_args_str(message)

    # dont support AFK as anon admin
    if message.from_user.id == 1087968824:
        await message.reply(strings["afk_anon"])
        return

    if not arg:
        reason = "No reason"
    else:
        reason = arg

    user = await get_user_by_id(message.from_user.id)
    user_afk = await db.afk.find_one({"user": user["user_id"]})
    if user_afk:
        return

    await db.afk.insert_one({"user": user["user_id"], "reason": reason})
    text = strings["is_afk"].format(
        user=(await get_user_link(user["user_id"])), reason=html.escape(reason)
    )
    await message.reply(text)


@register(f="text", allow_edited=False)
@get_strings_dec("afk")
async def check_afk(message, strings):
    if bool(message.reply_to_message):
        if message.reply_to_message.from_user.id in (1087968824, 777000):
            return
    if message.from_user.id in (1087968824, 777000):
        return
    user_afk = await db.afk.find_one({"user": message.from_user.id})
    if user_afk:
        afk_cmd = re.findall("^[!/]afk(.*)", message.text)
        if not afk_cmd:
            await message.reply(
                strings["unafk"].format(
                    user=(await get_user_link(message.from_user.id))
                )
            )
            await db.afk.delete_one({"_id": user_afk["_id"]})

    user = await get_user(message)
    if not user:
        return

    user_afk = await db.afk.find_one({"user": user["user_id"]})
    if user_afk:
        await message.reply(
            strings["is_afk"].format(
                user=(await get_user_link(user["user_id"])),
                reason=html.escape(user_afk["reason"]),
            )
        )
