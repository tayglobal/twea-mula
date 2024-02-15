from kms_utils import get_secret
import kydb
import boto3
import json
from datetime import datetime
import requests
from nacl.signing import VerifyKey
import inspect
import asyncio
from settings import (
    LAMBDA_FUNCTION_MAP,
    TABLE_MAP,
    CHANNEL_IDS,
    DISCORD_PUBLIC_KEY,
    APPLICATION_ID,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_SKIP_AUTH = False
_SKIP_MESSAGE = False

logger.debug("debug")
logger.info("info")
logger.warn("warning")

logger.info("getting discord token")
DISCORD_TOKEN = get_secret("DISCORD_TOKEN")

CCY_SYMBOLS = {"JPY": "¥", "GBP": "£"}
CCY_FLAG = {"JPY": "🇯🇵", "GBP": "🇬🇧"}


class command:
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        def f(self):
            if inspect.iscoroutinefunction(func):
                msg = asyncio.run(func(self))
            else:
                msg = func(self)

            res = self._send_message_to_webhook(msg)
            return res and res.text

        f.__command__ = self.name
        return f


def get_command(func):
    return getattr(func, "__command__", None)


class DiscordAuthenticationException(Exception):
    pass


def authenticate_request(event):
    if _SKIP_AUTH:
        logger.info("Skipping authentication in test")
    else:

        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

        signature = event["headers"]["x-signature-ed25519"]
        timestamp = event["headers"]["x-signature-timestamp"]
        body = event["body"]

        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))

    return json.loads(event["body"])


class Handler:
    def __init__(self, db, stage, payload):
        self.db = db
        self.stage = stage
        self.payload = payload

    def _send_message_to_webhook(self, msg):
        if isinstance(msg, dict):
            payload = msg
        else:
            payload = {"content": msg}

        logger.info("Sending payload")
        logger.info(payload)

        if _SKIP_MESSAGE:
            return

        webhook_url = self._create_webhook_url(self.payload["token"])

        res = requests.patch(webhook_url, json=payload)
        logger.info(res.status_code)
        logger.info(res.text)
        return res

    def _create_webhook_url(self, token):
        return f"https://discord.com/api/webhooks/{APPLICATION_ID}/{token}/messages/@original"

    @command("ping")
    def ping(self):
        return "pong"

    def _format_ccy(self, amount: float, ccy="JPY", include_flag=False):
        res = f"{amount:,.0f}" if ccy == "JPY" else f"{amount:,.2f}"
        flag = (CCY_FLAG[ccy] + " ") if include_flag else ""
        return flag + CCY_SYMBOLS[ccy] + res

    def _format_fx_rate(self, fx_rate: float):
        return f"{fx_rate:.2f}"

    def _get_fx_rate(self, from_ccy: str, to_ccy: str):
        # TODO: Support other ccy pairs
        assert from_ccy == "GBP" and to_ccy == "JPY"
        fx_path = f"/fx/{from_ccy}{to_ccy}"
        if not self.db.exists(fx_path):
            raise KeyError(
                f"FX rate not found. Please set rate at {fx_path}. Or use use Discord command /mula_fx_set"
            )

        return self.db[fx_path]

    @command("mula_add")
    def mula_add(self):
        logger.info(self.payload)
        who, amount, description = [x["value"] for x in self.payload["data"]["options"]]
        verb = "Added" if amount > 0 else "Subtracted"
        bal_path = "/balance/" + who
        old_balance = self.db[bal_path] if self.db.exists(bal_path) else 0
        new_balance = old_balance + amount
        fx_rate = self._get_fx_rate("GBP", "JPY")
        # TODO: Do not hardcode
        alt_ccy = "GBP"

        self.db[bal_path] = new_balance
        now = datetime.now()
        self.db[f"/transactions/{who}/{now}"] = {
            "who": who,
            "amount": amount,
            "description": description,
            "timestamp": now,
        }

        new_bal_str = self._format_ccy(new_balance)
        new_bal_str_flag = self._format_ccy(new_balance, include_flag=True)
        return {
            "embeds": [
                {
                    "title": f"New transaction Added",
                    "description": f"""Account: <@{who}>
{verb}: {self._format_ccy(abs(amount))}
Description: {description}
Old Balance: {self._format_ccy(old_balance)}
New Balance: **{new_bal_str_flag}**
Or in {alt_ccy}: {new_bal_str} ÷ {self._format_fx_rate(fx_rate)} = **{self._format_ccy(new_balance / fx_rate, alt_ccy, include_flag=True)}**
""",
                }
            ],
        }

    @command("mula_fx_set")
    def mula_fx_set(self):
        ccy_pair, fx_rate = [x["value"] for x in self.payload["data"]["options"]]
        self.db["/fx/" + ccy_pair] = fx_rate
        return f"FX rate of {ccy_pair} set to {fx_rate}"

    @command("mula_fx_ls")
    def mula_fx_ls(self):
        return "\n".join(
            [
                ": ".join((x, self._format_fx_rate(self.db["/fx/" + x])))
                for x in self.db.ls("/fx")
            ]
        )

    @command("mula_bal")
    def mula_bal(self):
        data = self.payload["data"]
        if "options" in data:
            who = data["options"][0]["value"]
        else:
            who = self.payload["member"]["user"]["id"]

        bal_path = "/balance/" + who
        local_bal = self.db[bal_path]
        local_bal_str = self._format_ccy(local_bal, include_flag=True)
        # TODO: Hardcode
        local_ccy = "JPY"
        alt_ccy = "GBP"
        alt_bal = local_bal / self._get_fx_rate(alt_ccy, local_ccy)
        alt_bal_str = self._format_ccy(alt_bal, alt_ccy, include_flag=True)

        return {
            "embeds": [
                {
                    "description": f"""Balance for <@{who}>:
{local_bal_str} | {alt_bal_str}
""",
                }
            ],
        }

    def send_message(self):
        # Send message to Discord using bot token
        payload = {}

        payload_fields = "embed", "components", "content"
        for field in payload_fields:
            val = self.payload.get(field)
            if val:
                payload[field] = val

        msg = self.payload.get("message")
        if msg:
            payload["content"] = msg

        return self._send_message_to_channel(self.payload["channel"], payload)

    def _send_message_to_channel(self, channel_name, payload):
        channel_id = CHANNEL_IDS["test" if self.stage == "uat" else channel_name]
        webhook_url = f"https://discord.com/api/channels/{channel_id}/messages"
        headers = {"Authorization": "Bot " + DISCORD_TOKEN}
        logger.info(f'Sending to "{channel_name}": {payload}')
        res = requests.post(webhook_url, json=payload, headers=headers)
        if res.status_code != 200:
            logger.info(res.status_code)
            logger.info(res.text)
            raise Exception("Failed to send message to Discord")

        return "OK"


class_attrs = (getattr(Handler, x) for x in dir(Handler))
mapping = {get_command(x): x for x in class_attrs if get_command(x)}


def handle(stage, payload):
    logger.info(payload)
    data = payload["data"]
    cmd = data.get("name")

    client = boto3.client("lambda")
    if cmd:
        client.invoke_async(
            FunctionName=LAMBDA_FUNCTION_MAP[stage],
            InvokeArgs=json.dumps(
                {
                    "async_func": cmd,
                    "payload": payload,
                    "requestContext": {"stage": stage},
                }
            ),
        )

        return f"Processing {cmd}..."

    custom_id = payload["data"]["custom_id"]
    cmd = custom_id.split(":", 1)[0]

    client.invoke_async(
        FunctionName=LAMBDA_FUNCTION_MAP[stage],
        InvokeArgs=json.dumps(
            {
                "async_func": cmd,
                "payload": payload,
                "requestContext": {"stage": stage},
            }
        ),
    )

    return f"Command {custom_id} sent..."


def lambda_handler(event, context):
    logger.info(event)
    # Just wake the lambda function up
    if not event.get("requestContext"):
        logger.info("Waking up")
        return "AWAKE"

    stage = event["requestContext"]["stage"]
    db = kydb.connect("dynamodb://" + TABLE_MAP[stage])
    async_func = event.get("async_func")

    if async_func:
        payload = event.get("payload", {})
        h = Handler(db, stage, payload)

        if async_func == "send_message":
            func_name = async_func
        else:
            class_attrs = ((x, getattr(Handler, x)) for x in dir(Handler))
            mapping = {get_command(v): k for k, v in class_attrs if get_command(v)}
            func_name = mapping[async_func]

        res = getattr(h, func_name)()
        return {"statusCode": 200, "body": json.dumps(res)}

    try:
        payload = authenticate_request(event)
    except Exception as e:
        logger.error("Failed to authenticate Discord request")
        logger.error(e)
        return {"statusCode": 401, "body": json.dumps("Bad Signature")}

    if payload["type"] == 1:
        logger.info("Recieved ping request. Responding type: 1")
        return {"statusCode": 200, "body": json.dumps({"type": 1})}

    res = {
        "type": 4,
        "data": {
            "tts": False,
            "content": handle(stage, payload),
        },
    }

    logger.info(f"res = {res}")

    return {"statusCode": 200, "body": json.dumps(res)}
