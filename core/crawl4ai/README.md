We have modified [crawl4ai](https://github.com/unclecode/crawl4ai) version 0.4.30 (a hidden version) to serve as our project's web crawler and preliminary parsing solution.

The main reason we chose to modify it rather than directly use the pypi package is that wiseflow and crawl4ai have fundamentally different content extraction strategies, which are determined by their product positioning. Simply put, Crawl4ai focuses on using LLMs for efficient web content extraction, while Wiseflow's "crawl-and-parse" strategy aims to parse content while crawling.

If we were to use Crawl4ai directly as a package, we would encounter two issues:

- We don't need half of its features (especially the multycrawl and deepcrawl features introduced in versions after 0.4.30).
- The processing and computations for those unused features are wasteful (they are executed but not utilized by wiseflow).

Frankly speaking, I'm not a big fan of this approach. However, it is necessary preparation for the upcoming 0.4.x versions. For more advanced crawling implementations (like those for social platforms, which we've discussed many times), wiseflow needs its own retrieval methods.

In any case, let's look forward to it and give a shout-out to Crawl4ai!
