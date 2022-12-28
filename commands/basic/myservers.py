import interactions
from pymongo import MongoClient
from python_aternos import Client as AternosClient
from python_aternos import Streams as AternosStreams
import os
import util.aternos_def as aternos_def


class MyServers(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="my-servers", description="See a list of your servers",
                                    scope=1035996955869986859)
    async def myservers(self, ctx: interactions.CommandContext):
        await ctx.defer()
        aternos = aternos_def.get_login(str(ctx.author.user.id))

        if aternos != "invalid_credentials" and aternos != "invalid_2fa" and aternos is not None:
            servers = aternos.list_servers()

            actionRow = interactions.ActionRow(components=[
                interactions.SelectMenu(custom_id="myservers", placeholder="Select a server",
                                        options=[interactions.SelectOption(label=server.address, value=server.address)
                                                 for server in servers])])

            await ctx.send("Select a server", components=[actionRow])
        else:
            await ctx.send("You are not logged in!")

    @interactions.extension_component("myservers")
    async def myservers_select(self, ctx: interactions.CommandContext, serverAddress: str):
        await ctx.defer()

        aternos = aternos_def.get_login(str(ctx.author.user.id))
        servers = aternos.list_servers()

        for server in servers:
            if server.address == serverAddress[0]:
                embed = interactions.Embed(
                    title=server.address,
                    description="Here are the details of your server.",
                    color=0x2B87D3,
                    fields=[
                        interactions.EmbedField(name="Status", value=f"**{server.status.upper()}**", inline=True),
                        interactions.EmbedField(name="Players", value=f"{server.players_count}/{server.slots}",
                                                inline=True),
                        interactions.EmbedField(name="Memory", value=f"{server.ram}MB", inline=True),
                        interactions.EmbedField(name="Edition",
                                                value=f"{server.version} {server.edition.name.capitalize()}, {server.software}",
                                                inline=True)
                    ]
                )

                aternos_def.select_server(str(ctx.author.user.id), server.address)

                if server.status == "offline":
                    action_row = interactions.ActionRow(components=[
                        interactions.Button(label="Start", custom_id="startserver",
                                            style=interactions.ButtonStyle.SUCCESS)])
                else:
                    action_row = interactions.ActionRow(components=[
                        interactions.Button(label="Stop", custom_id="stopserver",
                                            style=interactions.ButtonStyle.DANGER)])

                await ctx.send(embeds=[embed], components=[action_row])

    @interactions.extension_component("startserver")
    async def startserver(self, ctx: interactions.CommandContext):
        await ctx.defer()

        server = aternos_def.get_server(str(ctx.author.user.id), aternos_def.get_selected_server(str(ctx.author.user.id)))

        if server is not None:
            @server.wss().wssreceiver(AternosStreams.status)
            async def on_message(msg):
                print("received smth")
                print(msg)

            await server.wss(True).connect()
            server.start()
        else:
            await ctx.send("You are not logged in!")

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
