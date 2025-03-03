from crawl4ai.markdown_generation_strategy import *


class CustomMarkdownGenerator(DefaultMarkdownGenerator):
    def generate_markdown(
        self,
        cleaned_html: str,
        base_url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> MarkdownGenerationResult:
        """
        remove citation markdown generating process and content filter process
        wiseflow info extraction strategy is different from crawl4ai
        we just need raw markdown
        """
        try:
            # Initialize HTML2Text with default options for better conversion
            h = CustomHTML2Text(baseurl=base_url)
            default_options = {
                "body_width": 0,  # Disable text wrapping
                "ignore_emphasis": False,
                "ignore_links": False,
                "ignore_images": False,
                "protect_links": True,
                "single_line_break": True,
                "mark_code": True,
                "escape_snob": False,
            }

            # Update with custom options if provided
            if html2text_options:
                default_options.update(html2text_options)
            elif options:
                default_options.update(options)
            elif self.options:
                default_options.update(self.options)

            h.update_params(**default_options)

            # Ensure we have valid input
            if not cleaned_html:
                cleaned_html = ""
            elif not isinstance(cleaned_html, str):
                cleaned_html = str(cleaned_html)

            # Generate raw markdown
            try:
                raw_markdown = h.handle(cleaned_html)
            except Exception as e:
                raw_markdown = f"Error converting HTML to markdown: {str(e)}"

            raw_markdown = raw_markdown.replace("    ```", "```")

            # Convert links to citations
            markdown_with_citations: str = ""
            references_markdown: str = ""
            """
            if citations:
                try:
                    (
                        markdown_with_citations,
                        references_markdown,
                    ) = self.convert_links_to_citations(raw_markdown, base_url)
                except Exception as e:
                    markdown_with_citations = raw_markdown
                    references_markdown = f"Error generating citations: {str(e)}"
            """
            # Generate fit markdown if content filter is provided
            fit_markdown: Optional[str] = ""
            filtered_html: Optional[str] = ""
            """
            if content_filter or self.content_filter:
                try:
                    content_filter = content_filter or self.content_filter
                    filtered_html = content_filter.filter_content(cleaned_html)
                    filtered_html = "\n".join(
                        "<div>{}</div>".format(s) for s in filtered_html
                    )
                    fit_markdown = h.handle(filtered_html)
                except Exception as e:
                    fit_markdown = f"Error generating fit markdown: {str(e)}"
                    filtered_html = ""
            """
            return MarkdownGenerationResult(
                raw_markdown=raw_markdown or "",
                markdown_with_citations=markdown_with_citations or "",
                references_markdown=references_markdown or "",
                fit_markdown=fit_markdown or "",
                fit_html=filtered_html or "",
            )
        except Exception as e:
            # If anything fails, return empty strings with error message
            error_msg = f"Error in markdown generation: {str(e)}"
            return MarkdownGenerationResult(
                raw_markdown=error_msg,
                markdown_with_citations=error_msg,
                references_markdown="",
                fit_markdown="",
                fit_html="",
            )