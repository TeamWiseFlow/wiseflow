from .mp_crawler import mp_crawler
from .cryptotracker_crawler import cryptotracker_crawler
from .cryptopanic_crawler import cryptopanic_crawler
from .coinlive_crawler import coinlive_crawler


scraper_map = {
    "mp.weixin.qq.com": mp_crawler,
    "cryptotracker.com": cryptotracker_crawler,
    "www.coinlive.com": coinlive_crawler,
    "cryptopanic.com": cryptopanic_crawler,
}
