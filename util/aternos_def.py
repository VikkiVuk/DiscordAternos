import python_aternos
from pymongo import MongoClient
from python_aternos import Client as AternosClient
import os


def login(user_id, username, password, authcode=None):
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo["bot"]
    collection = db["user_logins"]

    try:
        AternosClient.from_credentials(username, password)
        collection.insert_one({"id": user_id, "username": username, "password": password})
        return "ok"
    except python_aternos.CredentialsError:
        return "invalid_credentials"
    except python_aternos.TokenError:
        return "invalid_2fa"
    except Exception as e:
        return None


def get_login(user_id):
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo["bot"]
    collection = db["user_logins"]
    user = collection.find_one({"id": user_id})

    try:
        if user is not None:
            aternos = AternosClient.from_credentials(user["username"], user["password"])
            return aternos
        else:
            return None
    except python_aternos.CredentialsError:
        return "invalid_credentials"
    except python_aternos.TokenError:
        return "invalid_2fa"
    except Exception as e:
        return None


def select_server(user_id, server_address):
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo["bot"]
    collection = db["user_logins"]
    user = collection.find({"id": user_id})

    if user is not None:
        collection.update_one({"id": user_id}, {"$set": {"selected_server": server_address}})
        return True
    else:
        return False


def get_selected_server(user_id):
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo["bot"]
    collection = db["user_logins"]
    user = collection.find_one({"id": user_id})

    if user is not None:
        return user["selected_server"]
    else:
        return False


def get_server(user_id, server_address):
    servers = get_login(user_id).list_servers()

    if servers is not None and servers != "invalid_credentials" and servers != "invalid_2fa":
        for server in servers:
            if server.address == server_address:
                return server
        return None
    else:
        return "failed_to_login"
