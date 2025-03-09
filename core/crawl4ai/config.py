from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Default provider, ONLY used when the extraction strategy is LLMExtractionStrategy
MODEL_REPO_BRANCH = "new-release-0.0.2"

# Threshold for the minimum number of word in a HTML tag to be considered
MIN_WORD_THRESHOLD = 1
IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD = 1

IMPORTANT_ATTRS = ["src", "href", "alt", "title", "width", "height"]
ONLY_TEXT_ELIGIBLE_TAGS = [
    "b",
    "i",
    "u",
    "span",
    "del",
    "ins",
    "sub",
    "sup",
    "strong",
    "em",
    "code",
    "kbd",
    "var",
    "s",
    "q",
    "abbr",
    "cite",
    "dfn",
    "time",
    "small",
    "mark",
]
SOCIAL_MEDIA_DOMAINS = [
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "instagram.com",
    "pinterest.com",
    "tiktok.com",
    "snapchat.com",
    "reddit.com",
]

# Threshold for the Image extraction - Range is 1 to 6
# Images are scored based on point based system, to filter based on usefulness. Points are assigned
# to each image based on the following aspects.
# If either height or width exceeds 150px
# If image size is greater than 10Kb
# If alt property is set
# If image format is in jpg, png or webp
# If image is in the first half of the total images extracted from the page
IMAGE_SCORE_THRESHOLD = 2

MAX_METRICS_HISTORY = 1000

NEED_MIGRATION = True
URL_LOG_SHORTEN_LENGTH = 30
SHOW_DEPRECATION_WARNINGS = True
SCREENSHOT_HEIGHT_TRESHOLD = 10000
PAGE_TIMEOUT = 60000
DOWNLOAD_PAGE_TIMEOUT = 60000
