import asyncio
from getpass import getpass

import aiohttp
from libdyson import DysonAccount


def get_cred():
    email = input("Email: ")
    password = getpass()
    country = input("Country: ")
    return email, password, country


async def main():
    loop = asyncio.get_running_loop()
    email, password, country = await loop.run_in_executor(None, get_cred)

    async with aiohttp.ClientSession() as session:
        account = DysonAccount(email, password, country, session)
        await account.async_login()

        devices = await account.async_devices()
        for device in devices:
            print()
            print(f"Serial: {device.serial}")
            print(f"Name: {device.name}")
            print(f"Credentials: {device.credentials}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
