import interactions
from pymongo import MongoClient
from python_aternos import Client as AternosClient
import util.aternos_def as aternos_def


class Login(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="start", description="Start a server you have access to", scope=1035996955869986859)
    async def login(self, ctx: interactions.CommandContext):
        await ctx.send("Starting server...")

        

def setup(client):
    Login(client)
