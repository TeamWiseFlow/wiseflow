import asyncio
from wis import search_with_engine
from tools.bing_search import search_with_bing
from pprint import pprint


async def main():
    search_query = "核设施退役治理"
    
    engines_to_use = ["arxiv", "github", "ebay"]

    tasks = []
    for engine_name in engines_to_use:
        tasks.append(search_with_engine(engine_name, search_query))

    all_results = await asyncio.gather(*tasks)

    for i, engine_name in enumerate(engines_to_use):
        print(f"\n--- Results from {engine_name.capitalize()} ---")
        articles, markdown, link_dict = all_results[i]
        if articles:
            print(f'got {len(articles)} articles')
            pprint(articles)
        if markdown:
            print(f'got {len(link_dict)} items')
            print(markdown)
            pprint(link_dict)
        print('-'*100)
    
    bing_markdown, bing_link_dict = await search_with_bing(search_query)
    print(f'got {len(bing_link_dict)} items')
    print(bing_markdown)
    pprint(bing_link_dict)

if __name__ == "__main__":
    asyncio.run(main())