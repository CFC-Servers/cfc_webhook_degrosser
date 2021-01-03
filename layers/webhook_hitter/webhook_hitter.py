import asyncio
import aiohttp

class WebhookHitter:
    async def _send_webhook(self, data, url):
        print(f"Attempting to send a webhook to '{url}'")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, json=data) as response:
                    response_code = response.status
                    print(f"Sent webhook to '{url}' with response code of '{response_code}'")

        except Exception as e:
            print(f"Got an error when sending webhook to '{url}'")
            print(e, e.__class__)

    async def send_webhooks(self, data, urls):
        return await asyncio.gather(*[self._send_webhook(data, url) for url in urls])
