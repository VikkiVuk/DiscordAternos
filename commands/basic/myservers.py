import interactions
from pymongo import MongoClient
from python_aternos import Client as AternosClient
import os


class MyServers(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="my-servers", description="See a list of your servers", scope=1035996955869986859)
    async def myservers(self, ctx: interactions.CommandContext):
        await ctx.defer()
        mongo = MongoClient(os.getenv("MONGO_URI"))
        db = mongo["bot"]
        collection = db["user_logins"]
        userId = str(ctx.author.user.id)
        login = collection.find_one({"id": userId})

        if login is not None:
            aternos = AternosClient.from_credentials(login["username"], login["password"])
            servers = aternos.list_servers()

            # make a selection menu with the servers as options
            actionRow = interactions.ActionRow(components=[
                interactions.SelectMenu(custom_id="myservers", placeholder="Select a server",
                                        options=[interactions.SelectOption(label=server.address, value=server.address)
                                                 for server in servers])])

            await ctx.send("Select a server", components=[actionRow])

    @interactions.extension_component("myservers")
    async def myservers_select(self, ctx: interactions.CommandContext, serverAddress: str):
        await ctx.defer()

        collection = MongoClient(os.getenv("MONGO_URI"))["bot"]["user_logins"]
        login = collection.find_one({"id": str(ctx.author.user.id)})
        aternos = AternosClient.from_credentials(login["username"], login["password"])
        servers = aternos.list_servers()

        for server in servers:
            if server.address == serverAddress[0]:
                embed = interactions.Embed(
                    title=server.address,
                    description="Here are the details of your server.",
                    color=0x2B87D3,
                    fields=[
                        interactions.EmbedField(name="Status", value=f"**{server.status.upper()}**", inline=True),
                        interactions.EmbedField(name="Players", value=f"{server.players_count}/{server.slots}", inline=True),
                        interactions.EmbedField(name="Memory", value=f"{server.ram}MB", inline=True),
                        interactions.EmbedField(name="Edition", value=f"{server.version} {server.edition.name.capitalize()}, {server.software}", inline=True)
                    ]
                )

                # make a button to start the server if it's not running already
                if server.status == "offline":
                    action_row = interactions.ActionRow(components=[interactions.Button(label="Start", custom_id="startserver", style=interactions.ButtonStyle.SUCCESS)])
                else:
                    action_row = interactions.ActionRow(components=[interactions.Button(label="Stop", custom_id="stopserver", style=interactions.ButtonStyle.DANGER)])

                await ctx.send(embeds=[embed], components=[action_row])

    @interactions.extension_component("startserver")
    async def startserver(self, ctx: interactions.CommandContext, value: str):
        await ctx.defer()

        print(value)

        collection = MongoClient(os.getenv("MONGO_URI"))["bot"]["user_logins"]
        login = collection.find_one({"id": str(ctx.author.user.id)})
        aternos = AternosClient.from_credentials(login["username"], login["password"])
        servers = aternos.list_servers()

        for server in servers:
            if server.address == value:
                server.start()

                await ctx.send("Server started!")

    @interactions.extension_component("stopserver")
    async def stopserver(self, ctx: interactions.CommandContext):
        await ctx.defer()

        collection = MongoClient(os.getenv("MONGO_URI"))["bot"]["user_logins"]
        login = collection.find_one({"id": str(ctx.author.user.id)})
        aternos = AternosClient.from_credentials(login["username"], login["password"])
        servers = aternos.list_servers()

        for server in servers:
            if server.address == ctx.message.embeds[0].title:
                server.stop()

                await ctx.send("Server stopped!")
def setup(client):
    MyServers(client)
