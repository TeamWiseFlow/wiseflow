The search engines section is entirely copied from the searxng project, retaining the core algorithms (request construction and response parsing), while making architectural changes in engineering to adapt to the wiseflow project requirements.

Original repo: https://github.com/searxng/searxng

Currently only arXiv, bing, ebay, github, wikipedia engines have been migrated, but wikipedia is unstable and often fails requests, so it's not enabled yet.

—— bigbrother666sh 2025-06-26

One more thing, this engineering refactoring process was also my first attempt at using the so-called Async Agent Coding approach, where I simultaneously used Google Jules, Manus, and Hailuo Agent for "horse racing", and finally used Amazon Q (claude4-sonnet) for verification and evaluation. The process was quite interesting, and interested folks can refer to this: https://github.com/bigbrother666sh/searxng/tree/feature/simplified-engine-architecture