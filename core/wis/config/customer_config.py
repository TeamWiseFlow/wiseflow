# max urls per task
MAX_URLS_PER_TASK = 300
# viewport width and height for browser
# determines the crawler ability
VIEWPORT_WIDTH = 1366
VIEWPORT_HEIGHT = 768
# browser can open how many urls at the same time
# make it bigger, you got more handling speed but can got more memory usage and more possiblity of read time out
# 6 is safe
MaxSessionPermit = 6
# whether you want llm to consider external links
# make it true, then wiseflow will never explore links outside your sources' domains
EXCLUDE_EXTERNAL_LINKS = True
# del any you never used
ALL_PLATFORMS = [
    "ks",
    "wb",
    "web", # also for search engines
]