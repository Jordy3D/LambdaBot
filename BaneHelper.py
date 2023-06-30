import time

def get_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


def has_role(member, roles):
    for role in member.roles:
        if role.name in roles:
            return True

    return False

def get_total_members(bot):
    total_members = 0

    for guild in bot.guilds:
        total_members += guild.member_count
    return total_members