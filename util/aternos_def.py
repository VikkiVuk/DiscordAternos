import python_aternos
from pymongo import MongoClient
from python_aternos import Client as AternosClient
import os


def login(user_id, username, password, authcode=None):
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo["bot"]
    collection = db["user_logins"]
    user = collection.find_one({"id": user_id})

    if user is not None:
        try:
            aternos = AternosClient.from_credentials(user["username"], user["password"])
            print(aternos.saved_session)
            return "ok"
        except python_aternos.CredentialsError:
            return "invalid_credentials"
        except python_aternos.TokenError:
            return "invalid_2fa"

    else:
        return None


def get_server(user_id, server_address):
    servers = login(user_id).list_servers()

    for server in servers:
        if server.address == server_address:
            return server

    return None

# function that can be used in another file  to get the server object
#
# import aternos_def
#
# server = aternos_def.get_server("user_id", "server_address")
# print(server.address)

