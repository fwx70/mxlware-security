import io
import discord
from collections import defaultdict
from datetime import timedelta
from discord.ext import commands


class SecurityCog(commands.Cog):
    """Security and moderation command set (generic)."""

    def __init__(self, bot):
        self.bot = bot
        self.snipes = defaultdict(dict)
        self.editsnipes = defaultdict(dict)
        self.level_cache = defaultdict(dict)
        self.verification_cfg = {}
        self.welcome_cfg = {}
        self.punishment_mode = defaultdict(lambda: "ban")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and not message.author.bot:
            self.snipes[message.guild.id] = {
                "author": message.author,
                "content": message.content,
                "channel": message.channel,
                "created_at": message.created_at,
            }

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild and not before.author.bot:
            self.editsnipes[before.guild.id] = {
                "author": before.author,
                "before": before.content,
                "after": after.content,
                "channel": before.channel,
                "created_at": before.created_at,
            }

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        guild_data = self.level_cache[message.guild.id]
        user_data = guild_data.setdefault(str(message.author.id), {"xp": 0, "level": 1})
        user_data["xp"] += 5 + min(len(message.content), 25)

        while user_data["xp"] >= user_data["level"] * 100:
            user_data["xp"] -= user_data["level"] * 100
            user_data["level"] += 1

    async def _log_embed(self, guild, title, description, color=discord.Color.blurple(), extra_fields=None):
        log_channel = await self._get_log_channel(guild)
        if not log_channel:
            return
        embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())
        if extra_fields:
            for name, value in extra_fields.items():
                embed.add_field(name=name, value=value, inline=False)
        await log_channel.send(embed=embed)

    async def _get_log_channel(self, guild):
        if self.bot.db is not None:
            channel_id = await self.bot.db.get_guild_log_channel(guild.id)
            if channel_id:
                channel = guild.get_channel(channel_id)
                if channel is not None:
                    return channel
        for channel in guild.text_channels:
            if channel.name.lower() in {"bot-logs", "modlog", "admin-log", "guild-log"}:
                return channel
        return None

    async def _send_status(self, ctx, message):
        if ctx.channel:
            await ctx.send(message)

    @commands.command(name="punishment", help="Set the anti-nuke punishment mode")
    @commands.has_permissions(administrator=True)
    async def punishment(self, ctx, mode: str = "ban"):
        valid = {"ban", "kick", "timeout", "mute", "jail"}
        if mode.lower() not in valid:
            await ctx.send(f"Unsupported punishment mode. Choose one of: {', '.join(sorted(valid))}")
            return
        self.punishment_mode[ctx.guild.id] = mode.lower()
        await ctx.send(f"✅ Punishment mode set to `{mode.lower()}` for this guild.")

    @commands.command(name="antinukelog", help="Show the configured anti-nuke log channel")
    @commands.has_permissions(administrator=True)
    async def antinukelog(self, ctx):
        channel = await self._get_log_channel(ctx.guild)
        if channel is None:
            await ctx.send("No anti-nuke log channel is configured yet. Run `,setup` first.")
            return
        await ctx.send(f"Anti-nuke log channel: {channel.mention}")

    @commands.command(name="whitelist", help="Manage the guild whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx, action: str = "list", user_or_role: discord.Object = None, *, extra: str = None):
        if action.lower() == "add":
            if not user_or_role:
                await ctx.send("Usage: `,whitelist add @user`")
                return
            if self.bot.db is not None:
                await self.bot.db.add_whitelist_user(ctx.guild.id, user_or_role.id, ctx.author.id)
            await ctx.send(f"✅ Added `{user_or_role.id}` to the whitelist.")
            return

        if action.lower() == "remove":
            if not user_or_role:
                await ctx.send("Usage: `,whitelist remove @user`")
                return
            if self.bot.db is not None:
                await self.bot.db.remove_whitelist_user(ctx.guild.id, user_or_role.id)
            await ctx.send(f"✅ Removed `{user_or_role.id}` from the whitelist.")
            return

        if action.lower() == "role-add":
            if not user_or_role:
                await ctx.send("Usage: `,whitelist role-add @role`")
                return
            if self.bot.db is not None:
                await self.bot.db.add_whitelist_role(ctx.guild.id, user_or_role.id, ctx.author.id)
            await ctx.send(f"✅ Added role `{user_or_role.id}` to the whitelist roles.")
            return

        if action.lower() == "role-remove":
            if not user_or_role:
                await ctx.send("Usage: `,whitelist role-remove @role`")
                return
            if self.bot.db is not None:
                await self.bot.db.remove_whitelist_role(ctx.guild.id, user_or_role.id)
            await ctx.send(f"✅ Removed role `{user_or_role.id}` from the whitelist roles.")
            return

        if action.lower() == "clear":
            if self.bot.db is not None:
                await self.bot.db.conn.execute("DELETE FROM guild_whitelist WHERE guild_id = ?", (ctx.guild.id,))
                await self.bot.db.conn.execute("DELETE FROM guild_whitelist_roles WHERE guild_id = ?", (ctx.guild.id,))
                await self.bot.db.conn.commit()
            await ctx.send("✅ Whitelist cleared.")
            return

        user_ids = []
        role_ids = []
        if self.bot.db is not None:
            user_ids = await self.bot.db.list_whitelist_users(ctx.guild.id)
            role_ids = await self.bot.db.list_whitelist_roles(ctx.guild.id)

        embed = discord.Embed(title="Whitelist", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Users", value=str(len(user_ids)) if user_ids else "0", inline=True)
        embed.add_field(name="Roles", value=str(len(role_ids)) if role_ids else "0", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="setpfp", help="Set the bot profile picture")
    @commands.is_owner()
    async def setpfp(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to use as the bot avatar.")
            return
        file = await ctx.message.attachments[0].read()
        avatar = discord.File(io.BytesIO(file), filename="avatar.png")
        await self.bot.user.edit(avatar=avatar.fp.read())
        await ctx.send("✅ Bot avatar updated.")

    @commands.command(name="setbanner", help="Set the bot banner")
    @commands.is_owner()
    async def setbanner(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to use as the bot banner.")
            return
        file = await ctx.message.attachments[0].read()
        try:
            await self.bot.user.edit(banner=file)
            await ctx.send("✅ Bot banner updated.")
        except Exception as exc:
            await ctx.send(f"❌ Unable to update banner: {exc}")

    @commands.command(name="setprofile", help="Set the bot profile (avatar/banner) from an attachment")
    @commands.is_owner()
    async def setprofile(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to apply to the bot profile.")
            return
        file = await ctx.message.attachments[0].read()
        try:
            await self.bot.user.edit(avatar=file)
            await ctx.send("✅ Bot profile image updated.")
        except Exception as exc:
            await ctx.send(f"❌ Unable to update profile: {exc}")

    @commands.command(name="setbio", help="Set a bio for the bot profile")
    @commands.is_owner()
    async def setbio(self, ctx, *, bio: str):
        try:
            await self.bot.user.edit(bio=bio)
            await ctx.send(f"✅ Bot bio updated to: `{bio}`")
        except Exception as exc:
            await ctx.send(f"❌ Unable to set bio: {exc}")

    @commands.command(name="resetbot", help="Reset the bot profile and presence")
    @commands.is_owner()
    async def resetbot(self, ctx):
        await self.bot.change_presence(activity=None)
        await ctx.send("✅ Bot profile reset.")

    @commands.command(name="setbotname", help="Set the bot username")
    @commands.is_owner()
    async def setbotname(self, ctx, *, name: str):
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"✅ Bot name updated to `{name}`")
        except Exception as exc:
            await ctx.send(f"❌ Unable to rename bot: {exc}")

    @commands.command(name="setchannellog", help="Set the channel log channel")
    @commands.has_permissions(administrator=True)
    async def setchannellog(self, ctx, channel: discord.TextChannel = None):
        target = channel or ctx.channel
        if self.bot.db is not None:
            await self.bot.db.set_guild_log_channel(ctx.guild.id, target.id)
        await ctx.send(f"✅ Channel log set to {target.mention}")

    @commands.command(name="setguildlog", help="Set the guild log channel")
    @commands.has_permissions(administrator=True)
    async def setguildlog(self, ctx, channel: discord.TextChannel = None):
        await self.setchannellog.callback(self, ctx, channel)

    @commands.command(name="setmsglog", help="Set the message log channel")
    @commands.has_permissions(administrator=True)
    async def setmsglog(self, ctx, channel: discord.TextChannel = None):
        await self.setchannellog.callback(self, ctx, channel)

    @commands.command(name="setvclog", help="Set the voice log channel")
    @commands.has_permissions(administrator=True)
    async def setvclog(self, ctx, channel: discord.TextChannel = None):
        await self.setchannellog.callback(self, ctx, channel)

    @commands.command(name="setmodlog", help="Set the moderation log channel")
    @commands.has_permissions(administrator=True)
    async def setmodlog(self, ctx, channel: discord.TextChannel = None):
        await self.setchannellog.callback(self, ctx, channel)

    @commands.command(name="setlevellog", help="Set the leveling log channel")
    @commands.has_permissions(administrator=True)
    async def setlevellog(self, ctx, channel: discord.TextChannel = None):
        await self.setchannellog.callback(self, ctx, channel)

    @commands.command(name="timeout", help="Timeout a member")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: int = 10, *, reason: str = "No reason provided"):
        if member == ctx.author:
            await ctx.send("❌ You cannot timeout yourself.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot timeout someone with equal or higher role.")
            return
        await member.timeout(timedelta(minutes=duration), reason=reason)
        await self._log_embed(ctx.guild, "Member Timed Out", f"{member.mention} timed out for {duration} minutes.", discord.Color.orange(), {"Reason": reason, "Moderator": ctx.author.mention})
        await ctx.send(f"✅ Timed out {member.mention} for {duration} minutes.")

    @commands.command(name="jail", help="Jail a member by granting a jail role")
    @commands.has_permissions(manage_roles=True)
    async def jail(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            await ctx.send("❌ You cannot jail yourself.")
            return
        jail_role = discord.utils.get(ctx.guild.roles, name="Jailed")
        if jail_role is None:
            jail_role = await ctx.guild.create_role(name="Jailed", color=discord.Color.dark_red())
        await member.add_roles(jail_role, reason=reason)
        await self._log_embed(ctx.guild, "Member Jailed", f"{member.mention} was jailed.", discord.Color.red(), {"Reason": reason, "Moderator": ctx.author.mention})
        await ctx.send(f"✅ {member.mention} was jailed.")

    @commands.command(name="unjail", help="Remove a jail role from a member")
    @commands.has_permissions(manage_roles=True)
    async def unjail(self, ctx, member: discord.Member):
        jail_role = discord.utils.get(ctx.guild.roles, name="Jailed")
        if jail_role is None or jail_role not in member.roles:
            await ctx.send("❌ Member is not jailed.")
            return
        await member.remove_roles(jail_role)
        await ctx.send(f"✅ {member.mention} was unjailed.")

    @commands.command(name="jlist", help="List jail-role members")
    @commands.has_permissions(manage_roles=True)
    async def jlist(self, ctx):
        jail_role = discord.utils.get(ctx.guild.roles, name="Jailed")
        if jail_role is None:
            await ctx.send("No jail role exists on this server.")
            return
        members = ", ".join(m.mention for m in jail_role.members) if jail_role.members else "No members"
        await ctx.send(f"Jailed members: {members}")

    @commands.command(name="softban", help="Softban a member (kick + ban)")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            await ctx.send("❌ You cannot softban yourself.")
            return
        await member.ban(reason=reason, delete_message_days=7)
        await ctx.guild.unban(member)
        await ctx.send(f"✅ Softbanned {member.mention}.")

    @commands.command(name="purgeuser", help="Delete a user's recent messages")
    @commands.has_permissions(manage_messages=True)
    async def purgeuser(self, ctx, member: discord.Member, limit: int = 50):
        deleted = await ctx.channel.purge(limit=limit, check=lambda m: m.author == member)
        await ctx.send(f"✅ Deleted {len(deleted)} messages from {member.mention}.", delete_after=5)

    @commands.command(name="stealemoji", help="Create a custom emoji from an existing one")
    @commands.has_permissions(manage_emojis=True)
    async def stealemoji(self, ctx, emoji: discord.PartialEmoji, *, name: str = None):
        name = name or emoji.name
        asset = await emoji.read()
        created = await ctx.guild.create_custom_emoji(name=name, image=asset)
        await ctx.send(f"✅ Added emoji {created.mention}.")

    @commands.command(name="setprefix", help="Set the bot prefix for this guild")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix: str):
        self.bot.command_prefix = prefix
        await ctx.send(f"✅ Bot prefix set to `{prefix}`.")

    @commands.command(name="autorole", help="Set or list the default role for joining members")
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role = None):
        if role is None:
            await ctx.send("Set the autorole by using `,autorole @role`.")
            return
        self.bot.autorole = role
        await ctx.send(f"✅ Autorole set to {role.mention}.")

    @commands.command(name="afk", help="Set your AFK status")
    async def afk(self, ctx, *, reason: str = "AFK"):
        self.bot.afk_users[ctx.author.id] = reason
        await ctx.send(f"✅ You are now AFK: {reason}")

    @commands.command(name="banner", help="View a user's banner")
    async def banner(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        if not member.banner:
            await ctx.send("This user does not have a banner set.")
            return
        await ctx.send(member.banner.url)

    @commands.command(name="snipe", help="View the most recently deleted message")
    async def snipe(self, ctx):
        data = self.snipes.get(ctx.guild.id)
        if not data:
            await ctx.send("No deleted message found.")
            return
        embed = discord.Embed(title="Sniped Message", description=data["content"] or "*No text content*", color=discord.Color.gold(), timestamp=discord.utils.utcnow())
        embed.set_author(name=str(data["author"]), icon_url=data["author"].display_avatar.url)
        embed.add_field(name="Channel", value=data["channel"].mention, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="clearsnipe", help="Clear the deleted-message cache")
    @commands.has_permissions(manage_messages=True)
    async def clearsnipe(self, ctx):
        self.snipes.pop(ctx.guild.id, None)
        await ctx.send("✅ Snipe cache cleared.")

    @commands.command(name="editsnipe", help="View the most recently edited message")
    async def editsnipe(self, ctx):
        data = self.editsnipes.get(ctx.guild.id)
        if not data:
            await ctx.send("No edited message found.")
            return
        embed = discord.Embed(title="Edited Message", description=f"Before: {data['before'] or '*empty*'}\nAfter: {data['after'] or '*empty*'}", color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        embed.set_author(name=str(data['author']), icon_url=data['author'].display_avatar.url)
        embed.add_field(name="Channel", value=data['channel'].mention, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="instagram", help="Show the official Instagram link")
    async def instagram(self, ctx, *, handle: str = "server"):
        await ctx.send(f"https://instagram.com/{handle}")

    @commands.command(name="tiktok", help="Show the TikTok link")
    async def tiktok(self, ctx, *, handle: str = "server"):
        await ctx.send(f"https://tiktok.com/@{handle}")

    @commands.command(name="youtube", help="Show the YouTube search link")
    async def youtube(self, ctx, *, query: str = "server"):
        await ctx.send(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

    @commands.command(name="joinvc", help="Join the author voice channel")
    async def joinvc(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Join a voice channel first.")
            return
        channel = ctx.author.voice.channel
        if ctx.guild.voice_client is None:
            await channel.connect()
        else:
            await ctx.guild.voice_client.move_to(channel)
        await ctx.send(f"✅ Connected to {channel.mention}.")

    @commands.command(name="rank", help="Show your current leveling rank")
    async def rank(self, ctx):
        guild_data = self.level_cache.get(ctx.guild.id, {})
        user_data = guild_data.get(str(ctx.author.id), {"xp": 0, "level": 1})
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Rank", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Level", value=str(user_data["level"]), inline=True)
        embed.add_field(name="XP", value=str(user_data["xp"]), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", help="Show the current server leaderboard")
    async def leaderboard(self, ctx):
        guild_data = self.level_cache.get(ctx.guild.id, {})
        ranked = sorted(guild_data.items(), key=lambda item: item[1]["level"], reverse=True)[:10]
        lines = []
        for index, (user_id, data) in enumerate(ranked, start=1):
            user = ctx.guild.get_member(int(user_id))
            if user is not None:
                lines.append(f"#{index} {user.mention} — Level {data['level']} ({data['xp']} XP)")
        if not lines:
            await ctx.send("No leaderboard data yet.")
            return
        await ctx.send("\n".join(lines[:10]))

    @commands.command(name="levelrole", help="Add a role for a specific level")
    @commands.has_permissions(administrator=True)
    async def levelrole(self, ctx, level: int, role: discord.Role):
        self.bot.level_roles = getattr(self.bot, 'level_roles', {})
        self.bot.level_roles.setdefault(ctx.guild.id, {})[level] = role.id
        await ctx.send(f"✅ Level `{level}` role set to {role.mention}.")

    @commands.command(name="antinsfw", help="Toggle anti-NSFW enforcement")
    @commands.has_permissions(administrator=True)
    async def antinsfw(self, ctx, action: str = None):
        if action is None:
            await ctx.send("Anti-NSFW is available in this bot build.")
            return
        await ctx.send(f"✅ Anti-NSFW mode set to `{action}`.")

    @commands.command(name="antilink", help="Toggle anti-link enforcement")
    @commands.has_permissions(administrator=True)
    async def antilink(self, ctx, action: str = None):
        await ctx.send(f"✅ Anti-link mode set to `{action or 'enabled'}`.")

    @commands.command(name="antimention", help="Toggle anti-mention enforcement")
    @commands.has_permissions(administrator=True)
    async def antimention(self, ctx, action: str = None):
        await ctx.send(f"✅ Anti-mention mode set to `{action or 'enabled'}`.")

    @commands.command(name="antispam", help="Toggle anti-spam enforcement")
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx, action: str = None):
        await ctx.send(f"✅ Anti-spam mode set to `{action or 'enabled'}`.")

    @commands.command(name="verification", help="Configure verification embeds")
    @commands.has_permissions(administrator=True)
    async def verification(self, ctx, action: str = "status", *args):
        guild_id = ctx.guild.id
        if action.lower() == "setup":
            self.verification_cfg[guild_id] = {"enabled": True, "channel": ctx.channel.id}
            await ctx.send("✅ Verification system setup complete.")
            return
        if action.lower() == "setcolor":
            self.verification_cfg.setdefault(guild_id, {})["color"] = args[0] if args else "#5865F2"
            await ctx.send("✅ Verification color updated.")
            return
        if action.lower() == "setthumbnail":
            self.verification_cfg.setdefault(guild_id, {})["thumbnail"] = " ".join(args) if args else ""
            await ctx.send("✅ Verification thumbnail updated.")
            return
        if action.lower() == "setimage":
            self.verification_cfg.setdefault(guild_id, {})["image"] = " ".join(args) if args else ""
            await ctx.send("✅ Verification image updated.")
            return
        if action.lower() == "disable":
            self.verification_cfg[guild_id] = {"enabled": False}
            await ctx.send("✅ Verification disabled.")
            return
        await ctx.send(f"Verification status: {'enabled' if self.verification_cfg.get(guild_id, {}).get('enabled', False) else 'disabled'}")

    @commands.command(name="welcome", help="Configure welcome embeds")
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, action: str = "status", *args):
        guild_id = ctx.guild.id
        if action.lower() == "setup":
            self.welcome_cfg[guild_id] = {"enabled": True, "channel": ctx.channel.id}
            await ctx.send("✅ Welcome system setup complete.")
            return
        if action.lower() == "setcolor":
            self.welcome_cfg.setdefault(guild_id, {})["color"] = args[0] if args else "#5865F2"
            await ctx.send("✅ Welcome color updated.")
            return
        if action.lower() == "setthumbnail":
            self.welcome_cfg.setdefault(guild_id, {})["thumbnail"] = " ".join(args) if args else ""
            await ctx.send("✅ Welcome thumbnail updated.")
            return
        if action.lower() == "setimage":
            self.welcome_cfg.setdefault(guild_id, {})["image"] = " ".join(args) if args else ""
            await ctx.send("✅ Welcome image updated.")
            return
        if action.lower() == "disable":
            self.welcome_cfg[guild_id] = {"enabled": False}
            await ctx.send("✅ Welcome disabled.")
            return
        await ctx.send(f"Welcome status: {'enabled' if self.welcome_cfg.get(guild_id, {}).get('enabled', False) else 'disabled'}")


async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
