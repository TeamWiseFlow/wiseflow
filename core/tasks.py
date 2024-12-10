import asyncio
from general_process import crawler, pb, wiseflow_logger

counter = 1


async def schedule_pipeline(interval):
    global counter
    while True:
        wiseflow_logger.info(f'task execute loop {counter}')
        sites = pb.read('sites', filter='activated=True')
        todo_urls = set()
        for site in sites:
            if not site['per_hours'] or not site['url']:
                continue
            if counter % site['per_hours'] == 0:
                wiseflow_logger.info(f"applying {site['url']}")
                todo_urls.add(site['url'].rstrip('/'))

        counter += 1
        await crawler.run(list(todo_urls))
        wiseflow_logger.info(f'task execute loop finished, work after {interval} seconds')
        await asyncio.sleep(interval)


async def main():
    interval_hours = 1
    interval_seconds = interval_hours * 60 * 60
    await schedule_pipeline(interval_seconds)

asyncio.run(main())
