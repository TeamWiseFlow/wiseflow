from abc import ABC, abstractmethod
import inspect
from typing import Any, List, Dict, Optional, Tuple, Pattern, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from enum import IntFlag, auto
from datetime import datetime

from .llmuse import *

from .utils import *  # noqa: F403
from .utils import (
    extract_xml_data,
    split_and_parse_json_objects,
)
from .base.crawl4ai_models import * # noqa: F403
from .base.crawl4ai_models import TokenUsage

from functools import partial
import regex as re
from bs4 import BeautifulSoup
from lxml import html, etree

# bigbrother666sh:
# for default case, we use a LLMExtractionStrategy to extract information fragments and the protion urls from the html
# the result should be a list of dicts, each dict contains the information fragment and the portion url in a dict format
# how many dicts you get depends on the length of the input html sections(which is come from the chunking strategy
# for special case, you can also use the LLMExtractionStrategy with a additional schema input which describe what you want to extract and the result format
# but for thess case, a JsonExtractionStrategy or RegexExtractionStrategy is more recommended if you can explore the xpath or regex pattern from the page source
# all the strategies need a chuncked html section as input, and the result format is list of dicts


class ExtractionStrategy(ABC):
    """
    Abstract base class for all extraction strategies.
    """

    def __init__(self, input_format: str = "cleaned_html", **kwargs):
        """
        Initialize the extraction strategy.

        Args:
            input_format: Content format to use for extraction.
                         Options: "html", "cleaned_html"
            **kwargs: Additional keyword arguments
        """
        self.input_format = input_format
        self.DEL = "<|DEL|>"
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def extract(self, url: str, html: str, *q, **kwargs) -> List[Dict[str, Any]]:
        """
        Extract meaningful blocks or chunks from the given HTML.

        :param url: The URL of the webpage.
        :param html: The HTML content of the webpage.
        :return: A list of extracted blocks or chunks.
        """
        pass

    def run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]:
        """
        Process sections of text in parallel by default.

        :param url: The URL of the webpage.
        :param sections: List of sections (strings) to process.
        :return: A list of processed JSON blocks.
        """
        extracted_content = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.extract, url, section, **kwargs)
                for section in sections
            ]
            for future in as_completed(futures):
                extracted_content.extend(future.result())
        return extracted_content


class NoExtractionStrategy(ExtractionStrategy):
    """
    A strategy that does not extract any meaningful content from the HTML. It simply returns the entire HTML as a single block.
    """

    def extract(self, url: str, html: str, *q, **kwargs) -> List[Dict[str, Any]]:
        """
        Extract meaningful blocks or chunks from the given HTML.
        """
        return [{"index": 0, "content": html}]

    def run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]:
        return [
            {"index": i, "tags": [], "content": section}
            for i, section in enumerate(sections)
        ]

#######################################################
# Strategies using LLM-based extraction for text data #
#######################################################
class LLMExtractionStrategy(ExtractionStrategy):
    """
    A strategy that uses an LLM to extract meaningful content from the HTML.
    modified special for extract related infos and links
    """
    _UNWANTED_PROPS = {
            'provider' : 'Instead, use llm_config=LLMConfig(provider="...")',
            'api_token' : 'Instead, use llm_config=LlMConfig(api_token="...")',
            'base_url' : 'Instead, use llm_config=LLMConfig(base_url="...")',
            'api_base' : 'Instead, use llm_config=LLMConfig(base_url="...")',
        }
    def __init__(
        self,
        model:str,
        focuspoint: str = None, 
        restrictions: str = None, 
        schema: dict = None,
        extra_args: dict = {},
        verbose: bool=False,
        logger=None,
        **kwargs
    ):
        self.input_format = 'markdown' # only consume markdown input
        super().__init__(input_format=self.input_format, verbose=verbose, **kwargs)

        # self.force_json_response = force_json_response # do not support in this version
        self.verbose = verbose
        self.logger = logger
        self.schema = schema
        self.usages = []  # Store individual usages
        self.total_usage = TokenUsage()  # Accumulated usage
        self.extract_func = partial(self.extract, model=model, extra_args=extra_args)
        if schema:
            self.schema_mode = True
            self.prompt = PROMPT_EXTRACT_SCHEMA_WITH_INSTRUCTION.replace('{SCHEMA}', schema) 
        else:
            self.schema_mode = False
            focus_statement = f"<focus_point>{focuspoint}</focus_point>"
            if restrictions:
                focus_statement += f"\nAdhering to the specified restrictions:\n<restrictions>{restrictions}</restrictions>"
            self.prompt = PROMPT_EXTRACT_BLOCKS.replace('{FOCUS_POINT}', focus_statement)

    def __setattr__(self, name, value):
        """Handle attribute setting."""
        # TODO: Planning to set properties dynamically based on the __init__ signature
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters  # Dictionary of parameter names and their details

        if name in self._UNWANTED_PROPS and value is not all_params[name].default:
            raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
        
        super().__setattr__(name, value)  
        
    def extract(self,
                messages: List[Dict[str, str]],
                model: str,
                extra_args: dict = {}) -> List[Dict[str, Any]]:

        response = perform_completion_with_backoff(
            messages=messages,
            model=model,
            temperature=0.1,
            **extra_args,
        )

        if response:
            # Track usage
            usage = TokenUsage(
                completion_tokens=response.usage.completion_tokens,
                prompt_tokens=response.usage.prompt_tokens,
                total_tokens=response.usage.total_tokens,
                completion_tokens_details=response.usage.completion_tokens_details.__dict__
                if response.usage.completion_tokens_details
                else {},
                prompt_tokens_details=response.usage.prompt_tokens_details.__dict__
                if response.usage.prompt_tokens_details
                else {},
            )
            self.usages.append(usage)

            # Update totals
            self.total_usage.completion_tokens += usage.completion_tokens
            self.total_usage.prompt_tokens += usage.prompt_tokens
            self.total_usage.total_tokens += usage.total_tokens

            response = response.choices[0].message.content
            if self.verbose:
                print(f"response: {response}")
            # schema mode parsing
            if self.schema_mode:
                try:
                    blocks = extract_xml_data(["result"], response)["result"]
                    if not blocks:
                        blocks = []
                    else:
                        blocks = json.loads(blocks)
                except Exception:
                    if self.logger:
                        self.logger.debug("Failed to parse schema mode response, fallback to use split_and_parse")
                    parsed, unparsed = split_and_parse_json_objects(
                        response.choices[0].message.content
                    )
                    blocks = parsed
                    if unparsed:
                        blocks.append(
                            {"tags": ["error"], "content": unparsed}
                        )
            # infos and links mode parsing
            else: 
                result = extract_xml_data(["info", "links"], response)
                blocks = [result]
            return blocks
        else:
            if self.logger:
                self.logger.error(f"failed to call LLM, error: {response}\ninput:\n {messages}")
            else:
                print(f"[LOG] failed to call LLM, error: {response}\ninput:\n {messages}")
            # Add error information to extracted_content
            return [
                {
                    "tags": ["error"],
                    "content": str(response),
                }
            ]

    def run(self, 
            url: str, 
            sections: List[str], 
            date_stamp: str = datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        ) -> List[Dict[str, Any]]:
        """
        Process sections sequentially with a delay for rate limiting issues, specifically for LLMExtractionStrategy.

        Args:
            url: The URL of the webpage.
            sections: List of sections (strings) to process.

        Returns:
            A list of extracted blocks or chunks.
        """
        date_time_notify = f"The additional information provided, use as needed: Today is {date_stamp}"
        extracted_content = []
        if self.schema_mode:
            msg_list = [
                self.prompt.replace('{URL}', url).replace('{HTML}', sec) + date_time_notify for sec in sections]
        else:
            msg_list = [
                self.prompt.replace('{HTML}', sec) + date_time_notify for sec in sections]

        with ThreadPoolExecutor(max_workers=int(os.getenv("LLM_CONCURRENT_NUMBER", 3))) as executor:
            futures = [
                executor.submit(self.extract_func, messages=[{"role": "user", "content": msg}])
                for msg in msg_list
            ]
            for future in as_completed(futures):
                try:
                    extracted_content.extend(future.result())
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error in thread execution: {e}")
                    else:
                        print(f"Error in thread execution: {e}")
                    # Add error information to extracted_content
                    extracted_content.append(
                        {
                            "tags": ["error"],
                            "content": str(e),
                            }
                        )
        self.show_usage() 
        return extracted_content

    def show_usage(self) -> None:
        """Print a detailed token usage report showing total and per-request usage."""
        if self.logger:
            self.logger.debug("Token Usage till now:")
            self.logger.debug(f"Completion: {self.total_usage.completion_tokens:>12,}")
            self.logger.debug(f"Prompt: {self.total_usage.prompt_tokens:>12,}")
            self.logger.debug(f"Total: {self.total_usage.total_tokens:>12,}")
        if self.verbose:
            print("\n=== Token Usage Summary ===")
            print(f"{'Type':<15} {'Count':>12}")
            print("-" * 30)
            print(f"{'Completion':<15} {self.total_usage.completion_tokens:>12,}")
            print(f"{'Prompt':<15} {self.total_usage.prompt_tokens:>12,}")
            print(f"{'Total':<15} {self.total_usage.total_tokens:>12,}")

            print("\n=== Usage History ===")
            print(f"{'Request #':<10} {'Completion':>12} {'Prompt':>12} {'Total':>12}")
            print("-" * 48)
            for i, usage in enumerate(self.usages, 1):
                print(
                f"{i:<10} {usage.completion_tokens:>12,} {usage.prompt_tokens:>12,} {usage.total_tokens:>12,}"
                )


#######################################################
# New extraction strategies for JSON-based extraction #
#######################################################
class JsonElementExtractionStrategy(ExtractionStrategy):
    """
    Abstract base class for extracting structured JSON from HTML content.

    How it works:
    1. Parses HTML content using the `_parse_html` method.
    2. Uses a schema to define base selectors, fields, and transformations.
    3. Extracts data hierarchically, supporting nested fields and lists.
    4. Handles computed fields with expressions or functions.

    Attributes:
        DEL (str): Delimiter used to combine HTML sections. Defaults to '\n'.
        schema (Dict[str, Any]): The schema defining the extraction rules.
        verbose (bool): Enables verbose logging for debugging purposes.

    Methods:
        extract(url, html_content, *q, **kwargs): Extracts structured data from HTML content.
        _extract_item(element, fields): Extracts fields from a single element.
        _extract_single_field(element, field): Extracts a single field based on its type.
        _apply_transform(value, transform): Applies a transformation to a value.
        _compute_field(item, field): Computes a field value using an expression or function.
        run(url, sections, *q, **kwargs): Combines HTML sections and runs the extraction strategy.

    Abstract Methods:
        _parse_html(html_content): Parses raw HTML into a structured format (e.g., BeautifulSoup or lxml).
        _get_base_elements(parsed_html, selector): Retrieves base elements using a selector.
        _get_elements(element, selector): Retrieves child elements using a selector.
        _get_element_text(element): Extracts text content from an element.
        _get_element_html(element): Extracts raw HTML from an element.
        _get_element_attribute(element, attribute): Extracts an attribute's value from an element.
    """

    DEL = "\n"

    def __init__(self, schema: Dict[str, Any], **kwargs):
        """
        Initialize the JSON element extraction strategy with a schema.

        Args:
            schema (Dict[str, Any]): The schema defining the extraction rules.
        """
        super().__init__(**kwargs)
        self.schema = schema
        self.verbose = kwargs.get("verbose", False)

    def extract(
        self, url: str, html_content: str, *q, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract structured data from HTML content.

        How it works:
        1. Parses the HTML content using the `_parse_html` method.
        2. Identifies base elements using the schema's base selector.
        3. Extracts fields from each base element using `_extract_item`.

        Args:
            url (str): The URL of the page being processed.
            html_content (str): The raw HTML content to parse and extract.
            *q: Additional positional arguments.
            **kwargs: Additional keyword arguments for custom extraction.

        Returns:
            List[Dict[str, Any]]: A list of extracted items, each represented as a dictionary.
        """

        parsed_html = self._parse_html(html_content)
        base_elements = self._get_base_elements(
            parsed_html, self.schema["baseSelector"]
        )

        results = []
        for element in base_elements:
            # Extract base element attributes
            item = {}
            if "baseFields" in self.schema:
                for field in self.schema["baseFields"]:
                    value = self._extract_single_field(element, field)
                    if value is not None:
                        item[field["name"]] = value

            # Extract child fields
            field_data = self._extract_item(element, self.schema["fields"])
            item.update(field_data)

            if item:
                results.append(item)

        return results

    @abstractmethod
    def _parse_html(self, html_content: str):
        """Parse HTML content into appropriate format"""
        pass

    @abstractmethod
    def _get_base_elements(self, parsed_html, selector: str):
        """Get all base elements using the selector"""
        pass

    @abstractmethod
    def _get_elements(self, element, selector: str):
        """Get child elements using the selector"""
        pass

    def _extract_field(self, element, field):
        try:
            if field["type"] == "nested":
                nested_elements = self._get_elements(element, field["selector"])
                nested_element = nested_elements[0] if nested_elements else None
                return (
                    self._extract_item(nested_element, field["fields"])
                    if nested_element
                    else {}
                )

            if field["type"] == "list":
                elements = self._get_elements(element, field["selector"])
                return [self._extract_list_item(el, field["fields"]) for el in elements]

            if field["type"] == "nested_list":
                elements = self._get_elements(element, field["selector"])
                return [self._extract_item(el, field["fields"]) for el in elements]

            return self._extract_single_field(element, field)
        except Exception as e:
            if self.verbose:
                print(f"Error extracting field {field['name']}: {str(e)}")
            return field.get("default")

    def _extract_single_field(self, element, field):
        """
        Extract a single field based on its type.

        How it works:
        1. Selects the target element using the field's selector.
        2. Extracts the field value based on its type (e.g., text, attribute, regex).
        3. Applies transformations if defined in the schema.

        Args:
            element: The base element to extract the field from.
            field (Dict[str, Any]): The field definition in the schema.

        Returns:
            Any: The extracted field value.
        """

        if "selector" in field:
            selected = self._get_elements(element, field["selector"])
            if not selected:
                return field.get("default")
            selected = selected[0]
        else:
            selected = element

        value = None
        if field["type"] == "text":
            value = self._get_element_text(selected)
        elif field["type"] == "attribute":
            value = self._get_element_attribute(selected, field["attribute"])
        elif field["type"] == "html":
            value = self._get_element_html(selected)
        elif field["type"] == "regex":
            text = self._get_element_text(selected)
            match = re.search(field["pattern"], text)
            value = match.group(1) if match else None

        if "transform" in field:
            value = self._apply_transform(value, field["transform"])

        return value if value is not None else field.get("default")

    def _extract_list_item(self, element, fields):
        item = {}
        for field in fields:
            value = self._extract_single_field(element, field)
            if value is not None:
                item[field["name"]] = value
        return item

    def _extract_item(self, element, fields):
        """
        Extracts fields from a given element.

        How it works:
        1. Iterates through the fields defined in the schema.
        2. Handles computed, single, and nested field types.
        3. Updates the item dictionary with extracted field values.

        Args:
            element: The base element to extract fields from.
            fields (List[Dict[str, Any]]): The list of fields to extract.

        Returns:
            Dict[str, Any]: A dictionary representing the extracted item.
        """

        item = {}
        for field in fields:
            if field["type"] == "computed":
                value = self._compute_field(item, field)
            else:
                value = self._extract_field(element, field)
            if value is not None:
                item[field["name"]] = value
        return item

    def _apply_transform(self, value, transform):
        """
        Apply a transformation to a value.

        How it works:
        1. Checks the transformation type (e.g., `lowercase`, `strip`).
        2. Applies the transformation to the value.
        3. Returns the transformed value.

        Args:
            value (str): The value to transform.
            transform (str): The type of transformation to apply.

        Returns:
            str: The transformed value.
        """

        if transform == "lowercase":
            return value.lower()
        elif transform == "uppercase":
            return value.upper()
        elif transform == "strip":
            return value.strip()
        return value

    def _compute_field(self, item, field):
        try:
            if "expression" in field:
                return eval(field["expression"], {}, item)
            elif "function" in field:
                return field["function"](item)
        except Exception as e:
            if self.verbose:
                print(f"Error computing field {field['name']}: {str(e)}")
            return field.get("default")

    def run(self, url: str, sections: List[str], *q, **kwargs) -> List[Dict[str, Any]]:
        """
        Run the extraction strategy on a combined HTML content.

        How it works:
        1. Combines multiple HTML sections using the `DEL` delimiter.
        2. Calls the `extract` method with the combined HTML.

        Args:
            url (str): The URL of the page being processed.
            sections (List[str]): A list of HTML sections.
            *q: Additional positional arguments.
            **kwargs: Additional keyword arguments for custom extraction.

        Returns:
            List[Dict[str, Any]]: A list of extracted items.
        """

        combined_html = self.DEL.join(sections)
        return self.extract(url, combined_html, **kwargs)

    @abstractmethod
    def _get_element_text(self, element) -> str:
        """Get text content from element"""
        pass

    @abstractmethod
    def _get_element_html(self, element) -> str:
        """Get HTML content from element"""
        pass

    @abstractmethod
    def _get_element_attribute(self, element, attribute: str):
        """Get attribute value from element"""
        pass

    _GENERATE_SCHEMA_UNWANTED_PROPS = {
        'provider': 'Instead, use llm_config=LLMConfig(provider="...")',
        'api_token': 'Instead, use llm_config=LlMConfig(api_token="...")',
    }

    @staticmethod
    def generate_schema(
        html: str,
        schema_type: str = "CSS", # or XPATH
        query: str = None,
        model: str = None,
        target_json_example: str = None,
        **kwargs
    ) -> dict:
        """
        Generate extraction schema from HTML content and optional query.
        
        Args:
            html (str): The HTML content to analyze
            query (str, optional): Natural language description of what data to extract
            provider (str): Legacy Parameter. LLM provider to use 
            api_token (str): Legacy Parameter. API token for LLM provider
            llm_config (LLMConfig): LLM configuration object
            prompt (str, optional): Custom prompt template to use
            **kwargs: Additional args passed to LLM processor
            
        Returns:
            dict: Generated schema following the JsonElementExtractionStrategy format
        """
        for name, message in JsonElementExtractionStrategy._GENERATE_SCHEMA_UNWANTED_PROPS.items():
            if locals()[name] is not None:
                raise AttributeError(f"Setting '{name}' is deprecated. {message}")
        
        # Use default or custom prompt
        prompt_template = JSON_SCHEMA_BUILDER if schema_type == "CSS" else JSON_SCHEMA_BUILDER_XPATH
        
        # Build the prompt
        system_message = {
            "role": "system", 
            "content": f"""You specialize in generating special JSON schemas for web scraping. This schema uses CSS or XPATH selectors to present a repetitive pattern in crawled HTML, such as a product in a product list or a search result item in a list of search results. We use this JSON schema to pass to a language model along with the HTML content to extract structured data from the HTML. The language model uses the JSON schema to extract data from the HTML and retrieve values for fields in the JSON schema, following the schema.

Generating this HTML manually is not feasible, so you need to generate the JSON schema using the HTML content. The HTML copied from the crawled website is provided below, which we believe contains the repetitive pattern.

# Schema main keys:
- name: This is the name of the schema.
- baseSelector: This is the CSS or XPATH selector that identifies the base element that contains all the repetitive patterns.
- baseFields: This is a list of fields that you extract from the base element itself.
- fields: This is a list of fields that you extract from the children of the base element. {{name, selector, type}} based on the type, you may have extra keys such as "attribute" when the type is "attribute".

# Extra Context:
In this context, the following items may or may not be present:
- Example of target JSON object: This is a sample of the final JSON object that we hope to extract from the HTML using the schema you are generating.
- Extra Instructions: This is optional instructions to consider when generating the schema provided by the user.
- Query or explanation of target/goal data item: This is a description of what data we are trying to extract from the HTML. This explanation means we're not sure about the rigid schema of the structures we want, so we leave it to you to use your expertise to create the best and most comprehensive structures aimed at maximizing data extraction from this page. You must ensure that you do not pick up nuances that may exist on a particular page. The focus should be on the data we are extracting, and it must be valid, safe, and robust based on the given HTML.

# What if there is no example of target JSON object and also no extra instructions or even no explanation of target/goal data item?
In this scenario, use your best judgment to generate the schema. You need to examine the content of the page and understand the data it provides. If the page contains repetitive data, such as lists of items, products, jobs, places, books, or movies, focus on one single item that repeats. If the page is a detailed page about one product or item, create a schema to extract the entire structured data. At this stage, you must think and decide for yourself. Try to maximize the number of fields that you can extract from the HTML.

# What are the instructions and details for this schema generation?
{prompt_template}"""
        }
        
        user_message = {
            "role": "user",
            "content": f"""
                HTML to analyze:
                ```html
                {html}
                ```
                """
        }

        if query:
            user_message["content"] += f"\n\n## Query or explanation of target/goal data item:\n{query}"
        if target_json_example:
            user_message["content"] += f"\n\n## Example of target JSON object:\n```json\n{target_json_example}\n```"

        if query and not target_json_example:
            user_message["content"] += """IMPORTANT: To remind you, in this process, we are not providing a rigid example of the adjacent objects we seek. We rely on your understanding of the explanation provided in the above section. Make sure to grasp what we are looking for and, based on that, create the best schema.."""
        elif not query and target_json_example:
            user_message["content"] += """IMPORTANT: Please remember that in this process, we provided a proper example of a target JSON object. Make sure to adhere to the structure and create a schema that exactly fits this example. If you find that some elements on the page do not match completely, vote for the majority."""
        elif not query and not target_json_example:
            user_message["content"] += """IMPORTANT: Since we neither have a query nor an example, it is crucial to rely solely on the HTML content provided. Leverage your expertise to determine the schema based on the repetitive patterns observed in the content."""
        
        user_message["content"] += """IMPORTANT: Ensure your schema remains reliable by avoiding selectors that appear to generate dynamically and are not dependable. You want a reliable schema, as it consistently returns the same data even after many page reloads.

        Analyze the HTML and generate a JSON schema that follows the specified format. Only output valid JSON schema, nothing else.
        """

        try:
            # Call LLM with backoff handling
            response = perform_completion_with_backoff(
                messages=[system_message, user_message],
                model=model,
                json_response = True,                
                extra_args=kwargs
            )
            
            # Extract and return schema
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Failed to generate schema: {str(e)}")

class JsonCssExtractionStrategy(JsonElementExtractionStrategy):
    """
    Concrete implementation of `JsonElementExtractionStrategy` using CSS selectors.

    How it works:
    1. Parses HTML content with BeautifulSoup.
    2. Selects elements using CSS selectors defined in the schema.
    3. Extracts field data and applies transformations as defined.

    Attributes:
        schema (Dict[str, Any]): The schema defining the extraction rules.
        verbose (bool): Enables verbose logging for debugging purposes.

    Methods:
        _parse_html(html_content): Parses HTML content into a BeautifulSoup object.
        _get_base_elements(parsed_html, selector): Selects base elements using a CSS selector.
        _get_elements(element, selector): Selects child elements using a CSS selector.
        _get_element_text(element): Extracts text content from a BeautifulSoup element.
        _get_element_html(element): Extracts the raw HTML content of a BeautifulSoup element.
        _get_element_attribute(element, attribute): Retrieves an attribute value from a BeautifulSoup element.
    """

    def __init__(self, schema: Dict[str, Any], **kwargs):
        kwargs["input_format"] = "html"  # Force HTML input
        super().__init__(schema, **kwargs)

    def _parse_html(self, html_content: str):
        # return BeautifulSoup(html_content, "html.parser")
        return BeautifulSoup(html_content, "lxml")

    def _get_base_elements(self, parsed_html, selector: str):
        return parsed_html.select(selector)

    def _get_elements(self, element, selector: str):
        # Return all matching elements using select() instead of select_one()
        # This ensures that we get all elements that match the selector, not just the first one
        return element.select(selector)

    def _get_element_text(self, element) -> str:
        return element.get_text(strip=True)

    def _get_element_html(self, element) -> str:
        return str(element)

    def _get_element_attribute(self, element, attribute: str):
        return element.get(attribute)

class JsonLxmlExtractionStrategy(JsonElementExtractionStrategy):
    def __init__(self, schema: Dict[str, Any], **kwargs):
        kwargs["input_format"] = "html"
        super().__init__(schema, **kwargs)
        self._selector_cache = {}
        self._xpath_cache = {}
        self._result_cache = {}
        
        # Control selector optimization strategy
        self.use_caching = kwargs.get("use_caching", True)
        self.optimize_common_patterns = kwargs.get("optimize_common_patterns", True)
        
        # Load lxml dependencies once
        from lxml import etree, html
        from lxml.cssselect import CSSSelector
        self.etree = etree
        self.html_parser = html
        self.CSSSelector = CSSSelector
    
    def _parse_html(self, html_content: str):
        """Parse HTML content with error recovery"""
        try:
            parser = self.etree.HTMLParser(recover=True, remove_blank_text=True)
            return self.etree.fromstring(html_content, parser)
        except Exception as e:
            if self.verbose:
                print(f"Error parsing HTML, falling back to alternative method: {e}")
            try:
                return self.html_parser.fromstring(html_content)
            except Exception as e2:
                if self.verbose:
                    print(f"Critical error parsing HTML: {e2}")
                # Create minimal document as fallback
                return self.etree.Element("html")
    
    def _optimize_selector(self, selector_str):
        """Optimize common selector patterns for better performance"""
        if not self.optimize_common_patterns:
            return selector_str
            
        # Handle td:nth-child(N) pattern which is very common in table scraping
        import re
        if re.search(r'td:nth-child\(\d+\)', selector_str):
            return selector_str  # Already handled specially in _apply_selector
            
        # Split complex selectors into parts for optimization
        parts = selector_str.split()
        if len(parts) <= 1:
            return selector_str
            
        # For very long selectors, consider using just the last specific part
        if len(parts) > 3 and any(p.startswith('.') or p.startswith('#') for p in parts):
            specific_parts = [p for p in parts if p.startswith('.') or p.startswith('#')]
            if specific_parts:
                return specific_parts[-1]  # Use most specific class/id selector
                
        return selector_str
    
    def _create_selector_function(self, selector_str):
        """Create a selector function that handles all edge cases"""
        original_selector = selector_str
        
        # Try to optimize the selector if appropriate
        if self.optimize_common_patterns:
            selector_str = self._optimize_selector(selector_str)
        
        try:
            # Attempt to compile the CSS selector
            compiled = self.CSSSelector(selector_str)
            xpath = compiled.path
            
            # Store XPath for later use
            self._xpath_cache[selector_str] = xpath
            
            # Create the wrapper function that implements the selection strategy
            def selector_func(element, context_sensitive=True):
                cache_key = None
                
                # Use result caching if enabled
                if self.use_caching:
                    # Create a cache key based on element and selector
                    element_id = element.get('id', '') or str(hash(element))
                    cache_key = f"{element_id}::{selector_str}"
                    
                    if cache_key in self._result_cache:
                        return self._result_cache[cache_key]
                
                results = []
                try:
                    # Strategy 1: Direct CSS selector application (fastest)
                    results = compiled(element)
                    
                    # If that fails and we need context sensitivity
                    if not results and context_sensitive:
                        # Strategy 2: Try XPath with context adjustment
                        context_xpath = self._make_context_sensitive_xpath(xpath, element)
                        if context_xpath:
                            results = element.xpath(context_xpath)
                        
                        # Strategy 3: Handle special case - nth-child
                        if not results and 'nth-child' in original_selector:
                            results = self._handle_nth_child_selector(element, original_selector)
                        
                        # Strategy 4: Direct descendant search for class/ID selectors
                        if not results:
                            results = self._fallback_class_id_search(element, original_selector)
                            
                        # Strategy 5: Last resort - tag name search for the final part
                        if not results:
                            parts = original_selector.split()
                            if parts:
                                last_part = parts[-1]
                                # Extract tag name from the selector
                                tag_match = re.match(r'^(\w+)', last_part)
                                if tag_match:
                                    tag_name = tag_match.group(1)
                                    results = element.xpath(f".//{tag_name}")
                    
                    # Cache results if caching is enabled
                    if self.use_caching and cache_key:
                        self._result_cache[cache_key] = results
                        
                except Exception as e:
                    if self.verbose:
                        print(f"Error applying selector '{selector_str}': {e}")
                
                return results
                
            return selector_func
            
        except Exception as e:
            if self.verbose:
                print(f"Error compiling selector '{selector_str}': {e}")
            
            # Fallback function for invalid selectors
            return lambda element, context_sensitive=True: []
    
    def _make_context_sensitive_xpath(self, xpath, element):
        """Convert absolute XPath to context-sensitive XPath"""
        try:
            # If starts with descendant-or-self, it's already context-sensitive
            if xpath.startswith('descendant-or-self::'):
                return xpath
                
            # Remove leading slash if present
            if xpath.startswith('/'):
                context_xpath = f".{xpath}"
            else:
                context_xpath = f".//{xpath}"
                
            # Validate the XPath by trying it
            try:
                element.xpath(context_xpath)
                return context_xpath
            except:
                # If that fails, try a simpler descendant search
                return f".//{xpath.split('/')[-1]}"
        except:
            return None
    
    def _handle_nth_child_selector(self, element, selector_str):
        """Special handling for nth-child selectors in tables"""
        import re
        results = []
        
        try:
            # Extract the column number from td:nth-child(N)
            match = re.search(r'td:nth-child\((\d+)\)', selector_str)
            if match:
                col_num = match.group(1)
                
                # Check if there's content after the nth-child part
                remaining_selector = selector_str.split(f"td:nth-child({col_num})", 1)[-1].strip()
                
                if remaining_selector:
                    # If there's a specific element we're looking for after the column
                    # Extract any tag names from the remaining selector
                    tag_match = re.search(r'(\w+)', remaining_selector)
                    tag_name = tag_match.group(1) if tag_match else '*'
                    results = element.xpath(f".//td[{col_num}]//{tag_name}")
                else:
                    # Just get the column cell
                    results = element.xpath(f".//td[{col_num}]")
        except Exception as e:
            if self.verbose:
                print(f"Error handling nth-child selector: {e}")
                
        return results
    
    def _fallback_class_id_search(self, element, selector_str):
        """Fallback to search by class or ID"""
        results = []
        
        try:
            # Extract class selectors (.classname)
            import re
            class_matches = re.findall(r'\.([a-zA-Z0-9_-]+)', selector_str)
            
            # Extract ID selectors (#idname)
            id_matches = re.findall(r'#([a-zA-Z0-9_-]+)', selector_str)
            
            # Try each class
            for class_name in class_matches:
                class_results = element.xpath(f".//*[contains(@class, '{class_name}')]")
                results.extend(class_results)
                
            # Try each ID (usually more specific)
            for id_name in id_matches:
                id_results = element.xpath(f".//*[@id='{id_name}']")
                results.extend(id_results)
        except Exception as e:
            if self.verbose:
                print(f"Error in fallback class/id search: {e}")
                
        return results
    
    def _get_selector(self, selector_str):
        """Get or create a selector function with caching"""
        if selector_str not in self._selector_cache:
            self._selector_cache[selector_str] = self._create_selector_function(selector_str)
        return self._selector_cache[selector_str]
    
    def _get_base_elements(self, parsed_html, selector: str):
        """Get all base elements using the selector"""
        selector_func = self._get_selector(selector)
        # For base elements, we don't need context sensitivity
        return selector_func(parsed_html, context_sensitive=False)
    
    def _get_elements(self, element, selector: str):
        """Get child elements using the selector with context sensitivity"""
        selector_func = self._get_selector(selector)
        return selector_func(element, context_sensitive=True)
    
    def _get_element_text(self, element) -> str:
        """Extract normalized text from element"""
        try:
            # Get all text nodes and normalize
            text = " ".join(t.strip() for t in element.xpath(".//text()") if t.strip())
            return text
        except Exception as e:
            if self.verbose:
                print(f"Error extracting text: {e}")
            # Fallback
            try:
                return element.text_content().strip()
            except:
                return ""
    
    def _get_element_html(self, element) -> str:
        """Get HTML string representation of element"""
        try:
            return self.etree.tostring(element, encoding='unicode', method='html')
        except Exception as e:
            if self.verbose:
                print(f"Error serializing HTML: {e}")
            return ""
    
    def _get_element_attribute(self, element, attribute: str):
        """Get attribute value safely"""
        try:
            return element.get(attribute)
        except Exception as e:
            if self.verbose:
                print(f"Error getting attribute '{attribute}': {e}")
            return None
            
    def _clear_caches(self):
        """Clear caches to free memory"""
        if self.use_caching:
            self._result_cache.clear()

class JsonLxmlExtractionStrategy_naive(JsonElementExtractionStrategy):
    def __init__(self, schema: Dict[str, Any], **kwargs):
        kwargs["input_format"] = "html"  # Force HTML input
        super().__init__(schema, **kwargs)
        self._selector_cache = {}
    
    def _parse_html(self, html_content: str):
        from lxml import etree
        parser = etree.HTMLParser(recover=True)
        return etree.fromstring(html_content, parser)
    
    def _get_selector(self, selector_str):
        """Get a selector function that works within the context of an element"""
        if selector_str not in self._selector_cache:
            from lxml.cssselect import CSSSelector
            try:
                # Store both the compiled selector and its xpath translation
                compiled = CSSSelector(selector_str)
                
                # Create a function that will apply this selector appropriately
                def select_func(element):
                    try:
                        # First attempt: direct CSS selector application
                        results = compiled(element)
                        if results:
                            return results
                        
                        # Second attempt: contextual XPath selection
                        # Convert the root-based XPath to a context-based XPath
                        xpath = compiled.path
                        
                        # If the XPath already starts with descendant-or-self, handle it specially
                        if xpath.startswith('descendant-or-self::'):
                            context_xpath = xpath
                        else:
                            # For normal XPath expressions, make them relative to current context
                            context_xpath = f"./{xpath.lstrip('/')}"
                        
                        results = element.xpath(context_xpath)
                        if results:
                            return results
                        
                        # Final fallback: simple descendant search for common patterns
                        if 'nth-child' in selector_str:
                            # Handle td:nth-child(N) pattern
                            import re
                            match = re.search(r'td:nth-child\((\d+)\)', selector_str)
                            if match:
                                col_num = match.group(1)
                                sub_selector = selector_str.split(')', 1)[-1].strip()
                                if sub_selector:
                                    return element.xpath(f".//td[{col_num}]//{sub_selector}")
                                else:
                                    return element.xpath(f".//td[{col_num}]")
                        
                        # Last resort: try each part of the selector separately
                        parts = selector_str.split()
                        if len(parts) > 1 and parts[-1]:
                            return element.xpath(f".//{parts[-1]}")
                            
                        return []
                    except Exception as e:
                        if self.verbose:
                            print(f"Error applying selector '{selector_str}': {e}")
                        return []
                
                self._selector_cache[selector_str] = select_func
            except Exception as e:
                if self.verbose:
                    print(f"Error compiling selector '{selector_str}': {e}")
                
                # Fallback function for invalid selectors
                def fallback_func(element):
                    return []
                
                self._selector_cache[selector_str] = fallback_func
                
        return self._selector_cache[selector_str]
    
    def _get_base_elements(self, parsed_html, selector: str):
        selector_func = self._get_selector(selector)
        return selector_func(parsed_html)
    
    def _get_elements(self, element, selector: str):
        selector_func = self._get_selector(selector)
        return selector_func(element)
    
    def _get_element_text(self, element) -> str:
        return "".join(element.xpath(".//text()")).strip()
    
    def _get_element_html(self, element) -> str:
        from lxml import etree
        return etree.tostring(element, encoding='unicode')
    
    def _get_element_attribute(self, element, attribute: str):
        return element.get(attribute)    

class JsonXPathExtractionStrategy(JsonElementExtractionStrategy):
    """
    Concrete implementation of `JsonElementExtractionStrategy` using XPath selectors.

    How it works:
    1. Parses HTML content into an lxml tree.
    2. Selects elements using XPath expressions.
    3. Converts CSS selectors to XPath when needed.

    Attributes:
        schema (Dict[str, Any]): The schema defining the extraction rules.
        verbose (bool): Enables verbose logging for debugging purposes.

    Methods:
        _parse_html(html_content): Parses HTML content into an lxml tree.
        _get_base_elements(parsed_html, selector): Selects base elements using an XPath selector.
        _css_to_xpath(css_selector): Converts a CSS selector to an XPath expression.
        _get_elements(element, selector): Selects child elements using an XPath selector.
        _get_element_text(element): Extracts text content from an lxml element.
        _get_element_html(element): Extracts the raw HTML content of an lxml element.
        _get_element_attribute(element, attribute): Retrieves an attribute value from an lxml element.
    """

    def __init__(self, schema: Dict[str, Any], **kwargs):
        kwargs["input_format"] = "html"  # Force HTML input
        super().__init__(schema, **kwargs)

    def _parse_html(self, html_content: str):
        return html.fromstring(html_content)

    def _get_base_elements(self, parsed_html, selector: str):
        return parsed_html.xpath(selector)

    def _css_to_xpath(self, css_selector: str) -> str:
        """Convert CSS selector to XPath if needed"""
        if "/" in css_selector:  # Already an XPath
            return css_selector
        return self._basic_css_to_xpath(css_selector)

    def _basic_css_to_xpath(self, css_selector: str) -> str:
        """Basic CSS to XPath conversion for common cases"""
        if " > " in css_selector:
            parts = css_selector.split(" > ")
            return "//" + "/".join(parts)
        if " " in css_selector:
            parts = css_selector.split(" ")
            return "//" + "//".join(parts)
        return "//" + css_selector

    def _get_elements(self, element, selector: str):
        xpath = self._css_to_xpath(selector)
        if not xpath.startswith("."):
            xpath = "." + xpath
        return element.xpath(xpath)

    def _get_element_text(self, element) -> str:
        return "".join(element.xpath(".//text()")).strip()

    def _get_element_html(self, element) -> str:
        return etree.tostring(element, encoding="unicode")

    def _get_element_attribute(self, element, attribute: str):
        return element.get(attribute)

#######################################################
# RegexExtractionStrategy
# Fast, zero-LLM extraction of common entities via regular expressions.
#######################################################

_CTRL = {c: rf"\x{ord(c):02x}" for c in map(chr, range(32)) if c not in "\t\n\r"}

_WB_FIX = re.compile(r"\x08")               # stray back-space   →   word-boundary
_NEEDS_ESCAPE = re.compile(r"(?<!\\)\\(?![\\u])")   # lone backslash

def _sanitize_schema(schema: Dict[str, str]) -> Dict[str, str]:
    """Fix common JSON-escape goofs coming from LLMs or manual edits."""
    safe = {}
    for label, pat in schema.items():
        # 1️⃣ replace accidental control chars (inc. the infamous back-space)
        pat = _WB_FIX.sub(r"\\b", pat).translate(_CTRL)

        # 2️⃣ double any single backslash that JSON kept single
        pat = _NEEDS_ESCAPE.sub(r"\\\\", pat)

        # 3️⃣ quick sanity compile
        try:
            re.compile(pat)
        except re.error as e:
            raise ValueError(f"Regex for '{label}' won’t compile after fix: {e}") from None

        safe[label] = pat
    return safe


class RegexExtractionStrategy(ExtractionStrategy):
    """
    A lean strategy that finds e-mails, phones, URLs, dates, money, etc.,
    using nothing but pre-compiled regular expressions.

    Extraction returns::

        {
            "url":   "<page-url>",
            "label": "<pattern-label>",
            "value": "<matched-string>",
            "span":  [start, end]
        }

    Only `generate_schema()` touches an LLM, extraction itself is pure Python.
    """

    # -------------------------------------------------------------- #
    # Built-in patterns exposed as IntFlag so callers can bit-OR them
    # -------------------------------------------------------------- #
    class _B(IntFlag):
        EMAIL           = auto()
        PHONE_INTL      = auto()
        PHONE_US        = auto()
        URL             = auto()
        IPV4            = auto()
        IPV6            = auto()
        UUID            = auto()
        CURRENCY        = auto()
        PERCENTAGE      = auto()
        NUMBER          = auto()
        DATE_ISO        = auto()
        DATE_US         = auto()
        TIME_24H        = auto()
        POSTAL_US       = auto()
        POSTAL_UK       = auto()
        HTML_COLOR_HEX  = auto()
        TWITTER_HANDLE  = auto()
        HASHTAG         = auto()
        MAC_ADDR        = auto()
        IBAN            = auto()
        CREDIT_CARD     = auto()
        NOTHING         = auto()
        ALL             = (
            EMAIL | PHONE_INTL | PHONE_US | URL | IPV4 | IPV6 | UUID
            | CURRENCY | PERCENTAGE | NUMBER | DATE_ISO | DATE_US | TIME_24H
            | POSTAL_US | POSTAL_UK | HTML_COLOR_HEX | TWITTER_HANDLE
            | HASHTAG | MAC_ADDR | IBAN | CREDIT_CARD
        )

    # user-friendly aliases  (RegexExtractionStrategy.Email, .IPv4, …)
    Email          = _B.EMAIL
    PhoneIntl      = _B.PHONE_INTL
    PhoneUS        = _B.PHONE_US
    Url            = _B.URL
    IPv4           = _B.IPV4
    IPv6           = _B.IPV6
    Uuid           = _B.UUID
    Currency       = _B.CURRENCY
    Percentage     = _B.PERCENTAGE
    Number         = _B.NUMBER
    DateIso        = _B.DATE_ISO
    DateUS         = _B.DATE_US
    Time24h        = _B.TIME_24H
    PostalUS       = _B.POSTAL_US
    PostalUK       = _B.POSTAL_UK
    HexColor       = _B.HTML_COLOR_HEX
    TwitterHandle  = _B.TWITTER_HANDLE
    Hashtag        = _B.HASHTAG
    MacAddr        = _B.MAC_ADDR
    Iban           = _B.IBAN
    CreditCard     = _B.CREDIT_CARD
    All            = _B.ALL
    Nothing        = _B(0)  # no patterns

    # ------------------------------------------------------------------ #
    # Built-in pattern catalog
    # ------------------------------------------------------------------ #
    DEFAULT_PATTERNS: Dict[str, str] = {
        # Communication
        "email":           r"[\w.+-]+@[\w-]+\.[\w.-]+",
        "phone_intl":      r"\+?\d[\d .()-]{7,}\d",
        "phone_us":        r"\(?\d{3}\)?[ -. ]?\d{3}[ -. ]?\d{4}",
        # Web
        "url":             r"https?://[^\s\"'<>]+",
        "ipv4":            r"(?:\d{1,3}\.){3}\d{1,3}",
        "ipv6":            r"[A-F0-9]{1,4}(?::[A-F0-9]{1,4}){7}",
        # IDs
        "uuid":            r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        # Money / numbers
        "currency":        r"(?:USD|EUR|RM|\$|€|£)\s?\d+(?:[.,]\d{2})?",
        "percentage":      r"\d+(?:\.\d+)?%",
        "number":          r"\b\d{1,3}(?:[,.\s]\d{3})*(?:\.\d+)?\b",
        # Dates / Times
        "date_iso":        r"\d{4}-\d{2}-\d{2}",
        "date_us":         r"\d{1,2}/\d{1,2}/\d{2,4}",
        "time_24h":        r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:[:.][0-5]\d)?\b",
        # Misc
        "postal_us":       r"\b\d{5}(?:-\d{4})?\b",
        "postal_uk":       r"\b[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b",
        "html_color_hex":  r"#[0-9A-Fa-f]{6}\b",
        "twitter_handle":  r"@[\w]{1,15}",
        "hashtag":         r"#[\w-]+",
        "mac_addr":        r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}",
        "iban":            r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}",
        "credit_card":     r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})\b",
    }

    _FLAGS = re.IGNORECASE | re.MULTILINE
    _UNWANTED_PROPS = {
        "provider": "Use llm_config instead",
        "api_token": "Use llm_config instead",
    }

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        pattern: "_B" = _B.NOTHING,
        *,
        custom: Optional[Union[Dict[str, str], List[Tuple[str, str]]]] = None,
        input_format: str = "cleaned_html",
        **kwargs,
    ) -> None:
        """
        Args:
            patterns: Custom patterns overriding or extending defaults.
                      Dict[label, regex] or list[tuple(label, regex)].
            input_format: "html", "markdown" or "text".
            **kwargs: Forwarded to ExtractionStrategy.
        """
        super().__init__(input_format=input_format, **kwargs)

        # 1️⃣  take only the requested built-ins
        merged: Dict[str, str] = {
            key: rx
            for key, rx in self.DEFAULT_PATTERNS.items()
            if getattr(self._B, key.upper()).value & pattern
        }

        # 2️⃣  apply user overrides / additions
        if custom:
            if isinstance(custom, dict):
                merged.update(custom)
            else:  # iterable of (label, regex)
                merged.update({lbl: rx for lbl, rx in custom})

        self._compiled: Dict[str, Pattern] = {
            lbl: re.compile(rx, self._FLAGS) for lbl, rx in merged.items()
        }

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #
    def extract(self, url: str, content: str, *q, **kw) -> List[Dict[str, Any]]:
        # text = self._plain_text(html)
        out: List[Dict[str, Any]] = []

        for label, cre in self._compiled.items():
            for m in cre.finditer(content):
                out.append(
                    {
                        "url": url,
                        "label": label,
                        "value": m.group(0),
                        "span": [m.start(), m.end()],
                    }
                )
        return out

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _plain_text(self, content: str) -> str:
        if self.input_format == "text":
            return content
        return BeautifulSoup(content, "lxml").get_text(" ", strip=True)

    # ------------------------------------------------------------------ #
    # LLM-assisted pattern generator
    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    # LLM-assisted one-off pattern builder
    # ------------------------------------------------------------------ #
    @staticmethod
    def generate_pattern(
        label: str,
        html: str,
        *,
        query: Optional[str] = None,
        examples: Optional[List[str]] = None,
        model: str = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Ask an LLM for a single page-specific regex and return
            {label: pattern}   ── ready for RegexExtractionStrategy(custom=…)
        """

        # ── guard deprecated kwargs
        for k in RegexExtractionStrategy._UNWANTED_PROPS:
            if k in kwargs:
                raise AttributeError(
                    f"{k} is deprecated, {RegexExtractionStrategy._UNWANTED_PROPS[k]}"
                )

        # ── system prompt – hardened
        system_msg = (
            "You are an expert Python-regex engineer.\n"
            f"Return **one** JSON object whose single key is exactly \"{label}\", "
            "and whose value is a raw-string regex pattern that works with "
            "the standard `re` module in Python.\n\n"
            "Strict rules (obey every bullet):\n"
            "• If a *user query* is supplied, treat it as the precise semantic target and optimise the "
            "  pattern to capture ONLY text that answers that query. If the query conflicts with the "
            "  sample HTML, the HTML wins.\n"
            "• Tailor the pattern to the *sample HTML* – reproduce its exact punctuation, spacing, "
            "  symbols, capitalisation, etc. Do **NOT** invent a generic form.\n"
            "• Keep it minimal and fast: avoid unnecessary capturing, prefer non-capturing `(?: … )`, "
            "  and guard against catastrophic backtracking.\n"
            "• Anchor with `^`, `$`, or `\\b` only when it genuinely improves precision.\n"
            "• Use inline flags like `(?i)` when needed; no verbose flag comments.\n"
            "• Output must be valid JSON – no markdown, code fences, comments, or extra keys.\n"
            "• The regex value must be a Python string literal: **double every backslash** "
            "(e.g. `\\\\b`, `\\\\d`, `\\\\\\\\`).\n\n"
            "Example valid output:\n"
            f"{{\"{label}\": \"(?:RM|rm)\\\\s?\\\\d{{1,3}}(?:,\\\\d{{3}})*(?:\\\\.\\\\d{{2}})?\"}}"
        )

        # ── user message: cropped HTML + optional hints
        user_parts = ["```html", html[:5000], "```"]  # protect token budget
        if query:
            user_parts.append(f"\n\n## Query\n{query.strip()}")
        if examples:
            user_parts.append("## Examples\n" + "\n".join(examples[:20]))
        user_msg = "\n\n".join(user_parts)

        # ── LLM call (with retry/backoff)
        resp = perform_completion_with_backoff(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
            model=model,
            json_response=True,
            extra_args=kwargs,
        )
        try:
            # ── clean & load JSON (fix common escape mistakes *before* json.loads)
            raw = resp.choices[0].message.content
            raw = raw.replace("\x08", "\\b")                     # stray back-space → \b
            raw = re.sub(r'(?<!\\)\\(?![\\u"])', r"\\\\", raw)   # lone \ → \\
            pattern_dict = json.loads(raw)
        except Exception as exc:
            raise ValueError(f"LLM did not return valid JSON: {raw}") from exc

        # quick sanity-compile
        for lbl, pat in pattern_dict.items():
            try:
                re.compile(pat)
            except re.error as e:
                raise ValueError(f"Invalid regex for '{lbl}': {e}") from None

        return pattern_dict
