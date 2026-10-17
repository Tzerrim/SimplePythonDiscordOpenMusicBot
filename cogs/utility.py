import discord
from discord.ext import commands

from config import PREFIX


class Utility(commands.Cog):
    """Bot status and server info commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is online",
        brief="Check if the bot is online",
        usage="ping",
    )
    async def ping(self, ctx):
        """Basic check if bot is alive"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong. Latency: {latency} ms')

    @commands.command()
    async def info(self, ctx):
        """Gather bot info on this server"""
        embed = discord.Embed(
            title="Bot info",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Server",
            value=f"**Name:** {ctx.guild.name}\n"
                  f"**ID:** {ctx.guild.id}\n"
                  f"**Members:** {ctx.guild.member_count}",
            inline=False
        )

        bot_member = ctx.guild.me
        permissions = ctx.channel.permissions_for(bot_member)

        embed.add_field(
            name="Bot permissions",
            value=f"**Read messages:** {'yes' if permissions.read_messages else 'no'}\n"
                  f"**Send messages:** {'yes' if permissions.send_messages else 'no'}\n"
                  f"**Manage messages:** {'yes' if permissions.manage_messages else 'no'}\n"
                  f"**Read history:** {'yes' if permissions.read_message_history else 'no'}",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def debug(self, ctx):
        """Gather debugging info"""
        await ctx.send(f'''
**Debug:**
Bot: {self.bot.user}
Bot ID: {self.bot.user.id}
Prefix: {PREFIX}
Latency: {round(self.bot.latency * 1000)}ms
Channel: #{ctx.channel.name}
Server: {ctx.guild.name}
Message ID: {ctx.message.id}
    ''')

    @commands.command()
    async def channels(self, ctx):
        """Show all channels"""
        try:
            text_channels = [c for c in ctx.guild.text_channels]
            voice_channels = [c for c in ctx.guild.voice_channels]

            embed = discord.Embed(
                title="Server channels",
                color=discord.Color.green()
            )

            if text_channels:
                embed.add_field(
                    name="Text channels",
                    value="\n".join([f"- {c.name} ({c.id})" for c in text_channels[:10]]),
                    inline=False
                )

            if voice_channels:
                embed.add_field(
                    name="Voice channels",
                    value="\n".join([f"- {c.name}" for c in voice_channels[:5]]),
                    inline=False
                )

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.author.send("Not enough permissions to send messages to this channel")

        except Exception as e:
            error_embed = discord.Embed(title="Execution failure", description=str(e), color=discord.Color.red())
            try:
                await ctx.send(embed=error_embed)
            except discord.Forbidden:
                await ctx.author.send(f"Error. Also not enough permissions to send messages to this channel: `{e}`")

async def setup(bot):
    await bot.add_cog(Utility(bot))
