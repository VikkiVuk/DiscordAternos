import os
import dotenv
import interactions

dotenv.load()

bot = interactions.Client(token=os.getenv("TOKEN"))

for folder in os.listdir("./commands"):
    for file in os.listdir(f"./commands/{folder}"):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load(f'commands.{folder}.{name}')

bot.start()
