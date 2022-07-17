import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from logging import getLogger
from db import MovieDb

# Set up logger
logger = getLogger('gunicorn.error')
logger.setLevel(getLogger('gunicorn.error').level)

Movies = MovieDb(os.environ.get("MOVEIS_DB_URI"), logger)

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True
# create discord client
client = nextcord.Client()
bot = commands.Bot(command_prefix='!', intents=intents)

# token from https://discordapp.com/developers
token = os.getenv("token")

# bot is ready


@bot.event
async def on_ready():
    try:
        logger.debug('nextcord Version: {}'.format(nextcord.__version__))
        logger.info(f"Logged in as {bot.user}[{bot.user.id}]")

    except Exception as e:
        logger.error(e)

# on new message


@bot.event
async def on_message(message: nextcord.Message):

    try:
        await bot.process_commands(message)
    except commands.errors.CommandNotFound as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)

    # print message content
    print(f"[{message.guild}\{message.channel}] {message.author}: {message.content}")


@bot.command(name="addMovie")
async def addMove(ctx: commands.Context) -> None:
    try:
        movie_name = ctx.message.content.split("!addMovie")[1]

        movie = {
            "moviename": movie_name,
            "watched": False
        }

        Movies.add_movie(movie=movie)
    except Exception as e:
        logger.error(e)
        await ctx.send(f"Failed to add {movie_name}, please try again later!")
    else:
        await ctx.send(f"successfully added {movie_name}!")


@bot.command(name="removeMovie")
async def removeMove(ctx: commands.Context) -> None:
    movie_name = ctx.message.content.split("!removeMovie")[1]


try:
    # start bot
    logger.info('Starting MovieBot')
    bot.run(token)
except KeyboardInterrupt:
    logger.info("Exit requested")
except Exception as e:
    logger.error(e)
