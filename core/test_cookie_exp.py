import asyncio
from wis.nodriver_helper import NodriverHelper


async def main():
    async with NodriverHelper("wb") as helper:
        header_string, user_agent = await helper.for_mc_login()
        print(header_string)
        print(user_agent)
        print("weibo test done")

    async with NodriverHelper("ks") as helper:
        header_string, user_agent = await helper.for_mc_login()
        print(header_string)
        print(user_agent)
        print("kuaishou test done")

asyncio.run(main()) 
