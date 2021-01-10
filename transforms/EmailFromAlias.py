import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from maltego_trx.entities import Email
from maltego_trx.transform import DiscoverableTransform
from validate_email import validate_email


class EmailFromAlias(DiscoverableTransform):

    @classmethod
    async def _find_valid_emails(cls, email_addresses):
        results = []

        def func(**kwargs):
            return kwargs['email_address'], validate_email(**kwargs)

        with ThreadPoolExecutor(max_workers=10) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    partial(
                        func,
                        email_address=email_address,
                        check_mx=True,
                        smtp_timeout=10,
                        dns_timeout=10,
                        debug=True
                        )
                )
                for email_address in email_addresses
            ]
        for result in await asyncio.gather(*futures):
            if result[1]:
                results.append(result[0])

        return results

    @classmethod
    async def _alias_to_email(cls, alias, response):
        with open('data/email_providers.txt', 'r') as file:
            providers = map(
                    lambda x: x.strip(),
                    file.readlines()
                    )
        for email_address in await cls._find_valid_emails(map(
                lambda x: alias + '@' + x,
                providers
                )):
            response.addEntity(Email, email_address)

    @classmethod
    def create_entities(cls, request, response):
        asyncio.run(cls._alias_to_email(request.Value, response))
