from wwd import *

"""
refer this to modify a custom scraper(actully is a CrawlerRunConfig)
1. config the extractor
2. config the md_generator
3. config the filter strategy: target_elements, exclude_all_images, remove_comments, excluded_tags, excluded_selector, remove_forms, exclude_domains, only_text
4. config other base options, particularly the proxy
"""

md_generator = DefaultMarkdownGenerator(
        options={
            "skip_internal_links": True,
            "escape_html": True,
            "include_sup_sub": True
        }
    )



# recommended to use the LXMLWebScrapingStrategy for efficient scraping, no need to config it
# if you just want some elements or just want to exclude some elements, directly config the CrawlerRunConfig with following options:
# target_elements, exclude_all_images, remove_comments, excluded_tags, excluded_selector, remove_forms, exclude_domains, only_text
# these options are automatically passed to the LXMLWebScrapingStrategy

crawler_config = CrawlerRunConfig(
    # session_id="my_session123",
    delay_before_return_html=1.0,
    word_count_threshold=10,
    # keep_data_attributes=True,
    scraping_strategy=LXMLWebScrapingStrategy(),
    markdown_generator=md_generator, 
    # wait_until='commit', 
    # simulate_user=True,
    magic=True, 
    scan_full_page=True,
    scroll_delay=0.5,
    # adjust_viewport_to_content=True,
    # verbose=False,
    # keep_data_attributes=True,
    # fetch_ssl_certificate=True,
    # image_score_threshold=3
)

