import asyncio

from json import loads
from webhook_hitter import WebhookHitter
from os import getenv

# { <form secret>: [<webhook url>] }
ALLOWED_FORMS = loads(getenv("FORMSPREE_ALLOWED_FORMS"))
ACK = { "statusCode": 204 }
LOOP = asyncio.get_event_loop()
WebhookHandler = WebhookHitter()

class FormSpreeDegrosser:
    async def receive(self, event):
        headers = event.get("headers", {})
        secret = headers.get("x-hook-secret")

        # If we get a valid secret handshake, we must confirm it
        if secret:
            print(f"Got a secret header: '{secret}'")

            if not ALLOWED_FORMS.get(secret):
                print("Invalid secret header! Ignoring!")
                return ACK

            print("Responding to secret handshake with 200")
            return {
                "statusCode": 200,
                "headers": { "x-hook-secret": secret }
            }

        payload = loads(event["body"])
        form_secret = payload.get("form")
        webhook_urls = ALLOWED_FORMS.get(form_secret)

        print(f"Form secret: '{form_secret}'")

        if not webhook_urls:
            print("Invalid form secret! Ignoring!")
            return ACK

        degrossed = self.format(payload)
        return await WebhookHandler.send_webhooks(degrossed, urls=webhook_urls)

    def format(self, payload):
        submission = payload["submission"]
        keys = payload["keys"]

        fields = []
        for question in keys:
            answer = submission[question]
            formed_question = question.replace("_", " ")

            field = {
                "name": formed_question,
                "value": answer
            }

            fields.append(field)

        embed = {
            "title": "New Form Submission",
            "color": 0x00a1c9,
            "fields": fields
        }

        webhook = {
            "content": "",
            "embeds": [embed]
        }

        return webhook

FormDegrosser = FormSpreeDegrosser()

def lambda_handler(event, context):
    return LOOP.run_until_complete(FormDegrosser.receive(event))
