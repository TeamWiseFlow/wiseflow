import nodriver as uc

async def main():

    browser = await uc.start(headless=True)
    page = await browser.get('https://www.nowsecure.nl')
    print(await page.get_content())

if __name__ == '__main__':
    # since asyncio.run never worked (for me)
    uc.loop().run_until_complete(main())
