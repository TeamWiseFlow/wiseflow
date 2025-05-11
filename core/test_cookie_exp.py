import asyncio
from wwd.nodriver_helper import NodriverHelper


async def main():
    async with NodriverHelper("wb") as helper:
        await helper.for_mc_login()
    print("weibo test done")

    async with NodriverHelper("ks") as helper:
        await helper.for_mc_login()
    print("kuaishou test done")

asyncio.run(main()) 
