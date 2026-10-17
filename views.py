import discord

from config import PREFIX

TRACKS_PER_PAGE = 20
EMBED_DESCRIPTION_LIMIT = 4096

def build_track_pages(files):
    """Split numbered track list into pages that fit in an embed description"""
    pages = []
    lines = []
    length = 0

    for i, filename in enumerate(files, 1):
        line = f"`{i}.` {discord.utils.escape_markdown(filename)}"[:EMBED_DESCRIPTION_LIMIT]
        if lines and (len(lines) >= TRACKS_PER_PAGE or length + len(line) + 1 > EMBED_DESCRIPTION_LIMIT):
            pages.append("\n".join(lines))
            lines = []
            length = 0
        lines.append(line)
        length += len(line) + 1

    if lines:
        pages.append("\n".join(lines))
    return pages

class TrackListView(discord.ui.View):
    """Previous/Next buttons for paging through the track list"""
    def __init__(self, pages, total):
        super().__init__(timeout=180)
        self.pages = pages
        self.total = total
        self.page = 0
        self.message = None
        self._update_buttons()

    def build_embed(self):
        embed = discord.Embed(
            title="Available tracks",
            description=self.pages[self.page],
            color=discord.Color.blue()
        )
        embed.set_footer(
            text=f"Page {self.page + 1}/{len(self.pages)} · Total: {self.total} files · "
                 f"Play with /play track:<number> or {PREFIX}play <number|name>"
        )
        return embed

    def _update_buttons(self):
        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = self.page >= len(self.pages) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        # Removing buttons once they stop responding
        if self.message:
            try:
                await self.message.edit(view=None)
            except discord.HTTPException:
                pass
