import requests
import json
from kms_utils import get_secret
from settings import APPLICATION_ID, GUILD_ID

DISCORD_TOKEN = get_secret('DISCORD_TOKEN')

def create_command(command):
    # Define the headers for the POST request
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }

    # Make the POST request
    response = requests.post(
        f'https://discord.com/api/v8/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands',
        headers=headers,
        data=json.dumps(command),
    )

    # Print the response
    print(response.status_code)
    print(response.json())


def delete_command(command_id):
    # Get your bot token
    token = get_secret('DISCORD_TOKEN')

    # Define the command
    command = {
        "name": "ping3",
        "description": "Just testing the slash commands",
    }

    # Define the headers for the POST request
    headers = {
        "Authorization": f"Bot {token}"
    }

    response = requests.delete(
        f"https://discord.com/api/v8/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands/{command_id}",
        headers=headers,
    )

    # Print the response
    print(response.status_code)

def create_ping():
    create_command({
        "name": "mula_ping",
        "description": "Ping the lambda function just to wake it up",
    })

def create_mula_add():
    create_command({
        "name": "mula_add",
        "description": "Add a transaction",

        "options": [
            {
                "name": "who",
                "description": "Who does the transaciton belong",
                "type": 6,
                "required": True
            },
            {
                "name": "amount",
                "description": "The amount on the transaction, could be positive or negative",
                "type": 10,
                "required": True
            },
            {
                "name": "description",
                "description": "Description of the transaction",
                "type": 3,
                "required": True
            },
        ],
    })

def create_mula_fx_set():
    create_command({
        "name": "mula_fx_set",
        "description": "Set the FX Rate of a Currency Pair",

        "options": [
            {
                "name": "ccy_pair",
                "description": "The currency pair to set the rate for",
                "type": 3,
                "required": True
            },
            {
                "name": "fx_rate",
                "description": "The FX Rate",
                "type": 10,
                "required": True
            },
        ],
    })

def create_mula_fx_set():
    create_command({
        "name": "mula_fx_ls",
        "description": "List the FX Rates",
    })

def create_mula_bal():
    create_command({
        "name": "mula_bal",
        "description": "Show the balance of a user",

        "options": [
            {
                "name": "who",
                "description": "The user",
                "type": 6,
                "required": False
            }
        ],
    })

if __name__ == '__main__':
    # create_ping()
    # create_mula_add()
    # create_mula_fx_set()
    # create_mula_fx_set()
    # delete_command(123456)
    create_mula_bal()
