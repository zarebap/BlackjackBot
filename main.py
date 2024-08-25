import discord, os, random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Button, View

cards_colours = ['hearts', 'diamonds', 'clover', 'spades']
cards_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
ids = [
    '1272895982371340325', '1272895849193803856', '1272895709737385984', '1272895585028014161',
    '1272895480376070164', '1272895395651125248', '1272895334116495443', '1272895241762115594',
    '1272895010509033564', '1272894782603006062', '1272894676852146229', '1272894726298927105',
    '1272894864237006910', '1272895967531765824', '1272895869225537557', '1272895782575407135',
    '1272895621342171158', '1272895514568032336', '1272895411631423529', '1272895347345195079',
    '1272895267238056037', '1272895023482146928', '1272894817403408446', '1272894697903358014',
    '1272894737187209237', '1272894881148305459', '1272895952512094311', '1272895896488775691',
    '1272895734156623967', '1272895646931750923', '1272895536231612446', '1272895429012623493',
    '1272895362893479966', '1272895285194133554', '1272895034290606150', '1272894831332556843',
    '1272894707160060056', '1272894746876051539', '1272894984537903165', '1272895917825196093',
    '1272895824715579486', '1272895677646504017', '1272895559270666250', '1272895448952209483',
    '1272895377317560341', '1272895316873576500', '1272895045644718172', '1272894999612358677',
    '1272894765792497767', '1272894649287311464', '1272894716655964170', '1272894851289190481',
]
deck = [(card, colour, ids[i]) for i, (card, colour ) in enumerate([(card, colour) for colour in cards_colours for card in cards_list])]

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def card_value(card):
    if card[0] in ['J', 'Q', 'K']:
        return 10
    elif card[0] == 'A':
        return 11
    else:
        return int(card[0])

class BlackjackView(View):
    def __init__(self, player_card, dealer_card, interaction):
        super().__init__()
        self.player_card = player_card
        self.dealer_card = dealer_card
        self.interaction = interaction

    async def update_game_state(self):
        player_score = sum(card_value(card) for card in self.player_card)
        dealer_score = sum(card_value(card) for card in self.dealer_card)

        if player_score > 21:
            embed = discord.Embed(title="Blackjack", description="Game Over - You Busted!", color=0xff0000)
            embed.add_field(
                name=f"You | {player_score} (Busted)",
                value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in self.player_card]),
                inline=False)
            embed.add_field(
                name=f"Dealer | {dealer_score}",
                value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in self.dealer_card]),
                inline=False)
            embed.set_footer(icon_url=bot.user.avatar.url, text=bot.user.name)
            embed.timestamp = self.interaction.created_at
            await self.interaction.followup.send(embed=embed)
            self.stop()  
        else:
            embed = discord.Embed(color=0xffff00)
            embed.set_author(icon_url=self.interaction.user.avatar.url, name=self.interaction.user.display_name)
            embed.title = "Blackjack"
            embed.add_field(
                name=f"You | {player_score}",
                value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in self.player_card]),
                inline=False)
            embed.add_field(
                name=f"Dealer | {card_value(self.dealer_card[0])} + ?",
                value=f"<:{self.dealer_card[0][0]}_of_{self.dealer_card[0][1]}:{self.dealer_card[0][2]}>"
                      f"<:card_back:1272988480753893449>",
                inline=False)
            embed.set_footer(icon_url=bot.user.avatar.url, text=bot.user.name)
            embed.timestamp = self.interaction.created_at
            await self.interaction.followup.send(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_card = deck.pop()
        self.player_card.append(new_card)
        await self.update_game_state()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Complete dealer's hand and determine the result
        while sum(card_value(card) for card in self.dealer_card) < 17:
            self.dealer_card.append(deck.pop())

        dealer_score = sum(card_value(card) for card in self.dealer_card)
        player_score = sum(card_value(card) for card in self.player_card)

        if dealer_score > 21 or player_score > dealer_score:
            result = "You Win!"
        elif dealer_score == player_score:
            result = "It's a Draw!"
        else:
            result = "Dealer Wins!"

        embed = discord.Embed(title="Blackjack", description=result, color=0x00ff00 if "Win" in result else 0xff0000)
        embed.add_field(
            name=f"You | {player_score}",
            value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in self.player_card]),
            inline=False)
        embed.add_field(
            name=f"Dealer | {dealer_score}",
            value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in self.dealer_card]),
            inline=False)
        embed.set_footer(icon_url=bot.user.avatar.url, text=bot.user.name)
        embed.timestamp = self.interaction.created_at
        await interaction.response.send_message(embed=embed)
        self.stop()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="blackjack", description="Start a game of blackjack")
async def blackjack(interaction: discord.Interaction):
    random.shuffle(deck)
    player_card = [deck.pop(), deck.pop()]
    dealer_card = [deck.pop(), deck.pop()]
    view = BlackjackView(player_card, dealer_card, interaction)

    embed = discord.Embed(color=0xffff00)
    embed.set_author(icon_url=interaction.user.avatar.url, name=interaction.user.display_name)
    embed.title = "Blackjack"
    embed.add_field(
        name=f"You | {sum(card_value(card) for card in player_card)}",
        value=" ".join([f"<:{card[0]}_of_{card[1]}:{card[2]}>" for card in player_card]),
        inline=False)
    embed.add_field(
        name=f"Dealer | {card_value(dealer_card[0])} + ?",
        value=f"<:{dealer_card[0][0]}_of_{dealer_card[0][1]}:{dealer_card[0][2]}>"
              f"<:card_back:1272988480753893449>",
        inline=False)
    embed.set_footer(icon_url=bot.user.avatar.url, text=bot.user.name)
    embed.timestamp = interaction.created_at

    await interaction.response.send_message(embed=embed, view=view)

bot.run(TOKEN)
