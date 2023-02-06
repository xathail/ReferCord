# Imports
import discord
from discord.ext import commands
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()
# Create Bot
intents = discord.Intents.none()
intents.members = True
intents.bot.invites = True 
bot = discord.Bot(intents=intents)

# Setup List
bot.invites = defaultdict(list, {})
referralamounts = {}

@bot.event
async def on_invite_create(invite):
    bot.invites[invite.inviter.id]+=[{url : invite.url, "uses": 0, "users": []}]
    update_invites_file()
# Returns Your Existing Invite
@bot.command(description="Responds with your invite.")
async def myinvites(ctx):
    author_id = str(ctx.author.id)
    my_invites = [i for i in bot.invites if author_id == i['author_id']]
    if not my_invites:
        return await ctx.respond("You don't have an invite.")
    embed = discord.Embed(title="Your invites", color="#934")
    for c,i in enumerate(my_invites):
        embed.add_field(name=f'{c}. {i["url"]}', value=f"**Uses**: {i['uses']}", inline=True)
    await ctx.respond(embed=embed)
        

# Load bot.Invites
def loadinvites():
    tmp_invites = defaultdict(list, {})
    try:
        with open("invites.txt") as f:
            for line in f:
                data = line.strip().split(";")
                author_id, invite_url, uses, *users = data
                tmp_invites[author_id] += [{"url": invite_url, "uses": int(uses), "users": [int(user) for user in users]}]
        bot.invites = tmp_invites
    except FileNotFoundError:
        pass
    print("Loaded invites")

# Update bot.Invites
def update_invites_file():
    with open("invites.txt", "w") as f:
        for author_id, invite_data in bot.invites.items():
            f.write(f"{author_id};{invite_data['url']};{invite_data['uses']};{';'.join(map(str, invite_data['users']))}1\n")

# On Join
@bot.event
async def on_member_join(member):
    print("member joined")
    guild_invites = await guild.invites()
    vanity = True
    for author_id, invite_datas in bot.invites.items():
        for c, invite in enumerate(invite_datas):
            g_invite = next((x for x in guild_invites if x.url == invite['url']), None)
            if g_invite and g_invite.uses > invite['uses']:
                bot.invites[author_id][c]["uses"] += 1
                bot.invites[author_id][c]["users"].append(member.id)
                update_invites_file()
                vanity = False
                break
    
    channel = bot.get_channel(os.getenv("WELCOME_CHANNEL")) 
    await channel.send(f"{member.mention} joined the server{' (possibly by vanity)' if vanity else ''}.")

# Gets The Inviter Of A User If They Joined From A Bot Invite
@bot.command(description="Responds with the inviter of the mentioned user.")
async def inviter(ctx, member: discord.Member):
    author_id = None
    for invite_author_id, invite_datas in bot.invites.items():
        k = False
        for invite in invite_datas:
            if member.id in invite["users"]:
                author_id = invite_author_id
                break
        if k:
            break
    if not author_id:
        return await ctx.respond("Could not find the inviter.")
    inviter = ctx.guild.get_member(int(author_id))
    await ctx.respond(f"{member.mention} was invited by {inviter.mention}")






# Add Referral Amount
@bot.command(description="Add an amount referred to the mentioned user.")
async def referraladd(ctx, member: discord.Member, amount: int):
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.respond("You do not have permission to use this command.")
        return
    member_id = str(member.id)
    if member_id not in referralamounts:
        referralamounts[member_id] = 0
    referralamounts[member_id] += amount
    updatereferral()
    await ctx.respond(f"${amount} has been added to {member.mention}'s referral amount.")

# Check Referral Amount
@bot.command(description="Responds with the referral amount of the mentioned user or the author if no user is specified.")
async def referralamount(ctx, member: discord.Member = None):
    member = member or ctx.author
    member_id = str(member.id)
    if member_id not in referralamounts:
        referralamounts[member_id] = 0
    await ctx.respond(f"{member.mention} has referred a total of ${referralamounts[member_id]}")

# Quickly Add Referral Amount
@bot.command(description="Add a referral amount to the inviter of the mentioned user.")
async def quickreferraladd(ctx, member: discord.Member, amount: int):
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.respond("You do not have permission to use this command.")
        return
    member_id = str(member.id)
    inviter = None
    for invite_author_id, invite_data in bot.invites.items():
        if member.id in invite_data["users"]:
            inviter = ctx.guild.get_member(int(invite_author_id))
            break
    if inviter is None:
        await ctx.respond("Could not find the inviter or the invite was not created through the bot.")
        return
    inviter_id = str(inviter.id)
    if inviter_id not in referralamounts:
        referralamounts[inviter_id] = 0
    referralamounts[inviter_id] += amount
    updatereferral()
    await ctx.respond(f"${amount} has been added to {inviter.mention}'s referral amount.")

# Function To Update Referral File
def updatereferral():
    with open("referralamounts.txt", "w") as f:
        for member_id, amount in referralamounts.items():
            f.write(f"{member_id};{amount}\n")

# Function To Load Referral File
def loadreferral():
    global referralamounts
    referralamounts = {}
    try:
        with open("referralamounts.txt") as f:
            for line in f:
                data = line.strip().split(";")
                member_id, amount = data
                referralamounts[member_id] = int(amount)
    except FileNotFoundError:
        pass
    print("Loaded Referral Amounts")

# Initialise Bot
loadreferral()
loadinvites()
bot.run(os.getenv("TOKEN"))
