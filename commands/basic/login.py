import interactions
from pymongo import MongoClient
from python_aternos import Client as AternosClient
import os
import util.aternos_def as aternos_def

class Login(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="login", description="Login to your Aternos account",
                                    scope=1035996955869986859)
    async def login(self, ctx: interactions.CommandContext):
        modal = interactions.Modal(
            custom_id="login",
            title="Login",
            components=[
                interactions.TextInput(style=interactions.TextStyleType.SHORT, label="Username", custom_id="username", required=True),
                interactions.TextInput(style=interactions.TextStyleType.SHORT, label="Password", custom_id="password", required=True),
                interactions.TextInput(style=interactions.TextStyleType.SHORT, label="2FA", custom_id="two_fa", required=False)
            ]
        )

        await ctx.popup(modal)

    @interactions.extension_modal("login")
    async def login_modal(self, ctx, username: str, password: str, two_fa: str):
        await ctx.defer()
        result = aternos_def.login(str(ctx.author.user.id), username, password, two_fa)

        if result == "ok":
            await ctx.send("Successfully logged in!")
        else:
            if result == "invalid_credentials":
                await ctx.send("Invalid credentials")
            elif result == "invalid_2fa":
                await ctx.send("Invalid 2FA code")
            else:
                await ctx.send("An error occurred")


def setup(client):
    Login(client)
