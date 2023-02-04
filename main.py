# Imports
import discord
from discord.ext import commands

# Create Bot
bot = discord.Bot(intents=discord.Intents.all())

# Setup List
invites = {}
referralamounts = {}

# Create Invites
@bot.command(description="Creates an invite for you.")
async def createinvite(ctx):
    author_id = str(ctx.author.id)
    if author_id in invites:
        await ctx.respond(f"You already have an invite: {invites[author_id]['url']} with {invites[author_id]['uses']} uses.")
        return
    invite = await ctx.channel.create_invite(max_uses=0)
    invites[author_id] = {"url": invite.url, "uses": 0, "users": []}
    update_invites_file()
    await ctx.respond(f"Here is your invite: {invite.url}")
    print("New Invite Created")

# Returns Your Existing Invite
@bot.command(description="Responds with your invite.")
async def myinvite(ctx):
    author_id = str(ctx.author.id)
    if author_id in invites:
        await ctx.respond(f"Your invite: {invites[author_id]['url']} has {invites[author_id]['uses']} uses.")
    else:
        await ctx.respond("You don't have an invite.")

# Load Invites
def loadinvites():
    global invites
    invites = {}

    try:
        with open("invites.txt") as f:
            for line in f:
                data = line.strip().split(";")
                author_id, invite_url, uses, *users = data
                invites[author_id] = {"url": invite_url, "uses": int(uses), "users": [int(user) for user in users]}
    except FileNotFoundError:
        pass
    print("Loaded Invites")

# Update Invites
def update_invites_file():
    with open("invites.txt", "w") as f:
        for author_id, invite_data in invites.items():
            f.write(f"{author_id};{invite_data['url']};{invite_data['uses']};{';'.join(map(str, invite_data['users']))}1\n")

# On Join
@bot.event
async def on_member_join(member):
    print("member joined")
    guild = member.guild
    invite = None
    invite_list = await guild.invites()
    most_recent = None
    max_timestamp = 0
    for inv in invite_list:
        if inv.uses > 0 and inv.created_at.timestamp() > max_timestamp:
            max_timestamp = inv.created_at.timestamp()
            most_recent = inv
    if most_recent:
        for author_id, invite_data in invites.items():
            if invite_data['url'] == most_recent.url:
                invites[author_id]["uses"] += 1
                invites[author_id]["users"].append(member.id)
                invited_by = guild.get_member(author_id)
                invites_amount = invite_data["uses"]
                break
    else:
        invited_by = None
        invites_amount = None
    update_invites_file()
    channel = bot.get_channel(1070649769707458590) # This Channel ID Can Be Changed To Any
    await channel.send(f"{member.mention} joined the server.")

# Gets The Inviter Of A User If They Joined From A Bot Invite
@bot.command(description="Responds with the inviter of the mentioned user.")
async def inviter(ctx, member: discord.Member):
    author_id = None
    for invite_author_id, invite_data in invites.items():
        if member.id in invite_data["users"]:
            author_id = invite_author_id
            break
    if author_id is None:
        await ctx.respond("Could not find the inviter.")
    else:
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
    if member is None:
        member = ctx.author
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
    for invite_author_id, invite_data in invites.items():
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
bot.run("TOKEN")
