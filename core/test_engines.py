import asyncio
from wis import search_with_engine
from pprint import pprint


async def main():
    search_query = "中国地区新建石材厂与石材设备采购信息"
    engines_to_use = ["ebay", "bing", "github", "arxiv"]

    tasks = []
    for engine_name in engines_to_use:
        tasks.append(search_with_engine(engine_name, search_query))

    all_results = await asyncio.gather(*tasks)

    for i, engine_name in enumerate(engines_to_use):
        print(f"\n--- Results from {engine_name.capitalize()} ---")
        print(f"length: {len(all_results[i])}")
        pprint(all_results[i])
        print("-" * 100)

if __name__ == "__main__":
    asyncio.run(main())