from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List
import os
from datetime import datetime
from urllib.parse import unquote
from rich.console import Console
from rich.text import Text
from loguru import logger as loguru_logger
from .utils import create_box_message


class LogLevel(Enum):
    DEFAULT = 0
    DEBUG = 1
    INFO = 2
    SUCCESS = 3
    WARNING = 4
    ERROR = 5
    CRITICAL = 6
    ALERT = 7
    NOTICE = 8
    EXCEPTION = 9
    FATAL = 10
    
    def __str__(self):
        return self.name.lower()

class LogColor(str, Enum):
    """Enum for log colors."""

    DEBUG = "lightblack"
    INFO = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    CYAN = "cyan"
    GREEN = "green"
    YELLOW = "yellow"
    MAGENTA = "magenta"
    DIM_MAGENTA = "dim magenta"

    def __str__(self):
        """Automatically convert rich color to string."""
        return self.value


class AsyncLoggerBase(ABC):
    @abstractmethod
    def debug(self, message: str, tag: str = "DEBUG", **kwargs):
        pass

    @abstractmethod
    def info(self, message: str, tag: str = "INFO", **kwargs):
        pass

    @abstractmethod
    def success(self, message: str, tag: str = "SUCCESS", **kwargs):
        pass

    @abstractmethod
    def warning(self, message: str, tag: str = "WARNING", **kwargs):
        pass

    @abstractmethod
    def error(self, message: str, tag: str = "ERROR", **kwargs):
        pass

    @abstractmethod
    def url_status(self, url: str, success: bool, timing: float, tag: str = "FETCH", url_length: int = 100):
        pass

    @abstractmethod
    def error_status(self, url: str, error: str, tag: str = "ERROR", url_length: int = 100):
        pass


class AsyncLogger(AsyncLoggerBase):
    """
    Asynchronous logger with support for colored console output and file logging.
    Supports templated messages with colored components.
    """

    DEFAULT_ICONS = {
        "INIT": "→",
        "READY": "✓",
        "FETCH": "↓",
        "SCRAPE": "◆",
        "EXTRACT": "■",
        "COMPLETE": "●",
        "ERROR": "×",
        "DEBUG": "⋯",
        "INFO": "ℹ",
        "WARNING": "⚠",
        "SUCCESS": "✔",
        "CRITICAL": "‼",
        "ALERT": "⚡",
        "NOTICE": "ℹ",
        "EXCEPTION": "❗",
        "FATAL": "☠",
        "DEFAULT": "•",
    }

    DEFAULT_COLORS = {
        LogLevel.DEBUG: LogColor.DEBUG,
        LogLevel.INFO: LogColor.INFO,
        LogLevel.SUCCESS: LogColor.SUCCESS,
        LogLevel.WARNING: LogColor.WARNING,
        LogLevel.ERROR: LogColor.ERROR,
    }

    def __init__(
        self,
        log_file: Optional[str] = None,
        log_level: Optional[LogLevel] = None,
        tag_width: int = 10,
        icons: Optional[Dict[str, str]] = None,
        colors: Optional[Dict[LogLevel, LogColor]] = None,
        verbose: bool = False,
    ):
        """
        Initialize the logger.

        Args:
            log_file: Optional file path for logging
            log_level: Minimum log level to display
            tag_width: Width for tag formatting
            icons: Custom icons for different tags
            colors: Custom colors for different log levels
            verbose: Whether to output to console
        """
        self.log_file = log_file
        if log_level is None:
            log_level = LogLevel.DEBUG if verbose else LogLevel.INFO
        self.log_level = log_level
        self.tag_width = tag_width
        self.icons = icons or self.DEFAULT_ICONS
        self.colors = colors or self.DEFAULT_COLORS
        self.verbose = verbose
        self.console = Console()

        # Initialize loguru logger for async file writing
        self.loguru = loguru_logger.bind()
        if log_file:
            # Create log file directory if needed
            # os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            # Remove default handler and add file sink with async processing
            self.loguru.remove()
            self.loguru.add(
                log_file,
                level="DEBUG" if self.log_level == LogLevel.DEBUG else "INFO",
                backtrace=True,
                diagnose=True,
                rotation="12 MB",
                enqueue=True,  # Enable async file writing
                encoding="utf-8"
            )

    def _format_tag(self, tag: str) -> str:
        """Format a tag with consistent width."""
        return f"[{tag}]".ljust(self.tag_width, ".")

    def _get_icon(self, tag: str) -> str:
        """Get the icon for a tag, defaulting to info icon if not found."""
        return self.icons.get(tag, self.icons["INFO"])
    
    def _shorten(self, text, length, placeholder="..."):
        """Truncate text in the middle if longer than length, or pad if shorter."""
        if len(text) <= length:
            return text.ljust(length)  # Pad with spaces to reach desired length
        half = (length - len(placeholder)) // 2
        shortened = text[:half] + placeholder + text[-half:]
        return shortened.ljust(length)  # Also pad shortened text to consistent length

    def _log(
        self,
        level: LogLevel,
        message: str,
        tag: str,
        params: Optional[Dict[str, Any]] = None,
        colors: Optional[Dict[str, LogColor]] = None,
        boxes: Optional[List[str]] = None,
        base_color: Optional[LogColor] = None
    ):
        """
        Core logging method that handles message formatting and output.

        Args:
            level: Log level for this message
            message: Message template string
            tag: Tag for the message
            params: Parameters to format into the message
            colors: Color overrides for specific parameters
            boxes: Box overrides for specific parameters
            base_color: Base color for the entire message
        """
        if level.value < self.log_level.value:
            return

        # avoid conflict with rich formatting
        parsed_message = message.replace("[", "[[").replace("]", "]]")
        if params:
            # FIXME: If there are formatting strings in floating point format, 
            # this may result in colors and boxes not being applied properly.
            # such as {value:.2f}, the value is 0.23333 format it to 0.23,
            # but we replace("0.23333", "[color]0.23333[/color]")
            formatted_message = parsed_message.format(**params)
            for key, value in params.items():
                # value_str may discard `[` and `]`, so we need to replace it. 
                value_str = str(value).replace("[", "[[").replace("]", "]]")
                # check is need apply color
                if colors and key in colors:
                    color_str = f"[{colors[key]}]{value_str}[/{colors[key]}]"
                    formatted_message = formatted_message.replace(value_str, color_str)
                    value_str = color_str

                # check is need apply box
                if boxes and key in boxes:
                    formatted_message = formatted_message.replace(value_str,
                        create_box_message(value_str, type=str(level)))

        else:
            formatted_message = parsed_message

        # Construct the full log line
        color: LogColor = base_color or self.colors[level]
        log_line = f"[{color}]{self._format_tag(tag)} {self._get_icon(tag)} {formatted_message} [/{color}]"

        self.console.print(log_line)

    def debug(self, message: str, tag: str = "DEBUG", params: Optional[Dict[str, Any]] = None):
        """Log a debug message."""
        if self.log_file:
            self.loguru.debug(message.format(**params))

        if self.verbose:
            self._log(LogLevel.DEBUG, message, tag, params=params)

    def info(self, message: str, tag: str = "INFO", params: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        if self.log_file:
            self.loguru.info(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.INFO, message, tag, params=params)

    def success(self, message: str, tag: str = "SUCCESS", params: Optional[Dict[str, Any]] = None):
        """Log a success message."""
        if self.log_file:
            self.loguru.info(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.SUCCESS, message, tag, params=params)

    def warning(self, message: str, tag: str = "WARNING", params: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        if self.log_file:
            self.loguru.warning(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.WARNING, message, tag, params=params)
        
    def critical(self, message: str, tag: str = "CRITICAL", params: Optional[Dict[str, Any]] = None):
        """Log a critical message."""
        if self.log_file:
            self.loguru.critical(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.CRITICAL, message, tag, params=params)
            
    def exception(self, message: str, tag: str = "EXCEPTION", params: Optional[Dict[str, Any]] = None):
        """Log an exception message."""
        if self.log_file:
            self.loguru.error(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.EXCEPTION, message, tag, params=params)
            
    def fatal(self, message: str, tag: str = "FATAL", params: Optional[Dict[str, Any]] = None):
        """Log a fatal message."""
        if self.log_file:
            self.loguru.critical(message.format(**params))

        if self.verbose:
            self._log(LogLevel.FATAL, message, tag, params=params)
            
    def alert(self, message: str, tag: str = "ALERT", params: Optional[Dict[str, Any]] = None):
        """Log an alert message."""
        if self.log_file:
            self.loguru.warning(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.ALERT, message, tag, params=params)
            
    def notice(self, message: str, tag: str = "NOTICE", params: Optional[Dict[str, Any]] = None):
        """Log a notice message."""
        if self.log_file:
            self.loguru.info(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.NOTICE, message, tag, params=params)

    def error(self, message: str, tag: str = "ERROR", params: Optional[Dict[str, Any]] = None):
        """Log an error message."""
        if self.log_file:
            self.loguru.error(message.format(**params))
            
        if self.verbose:
            self._log(LogLevel.ERROR, message, tag, params=params)

    def url_status(
        self,
        url: str,
        success: bool,
        timing: float,
        tag: str = "FETCH",
        url_length: int = 100,
    ):
        """
        Convenience method for logging URL fetch status.

        Args:
            url: The URL being processed
            success: Whether the operation was successful
            timing: Time taken for the operation
            tag: Tag for the message
            url_length: Maximum length for URL in log
        """
        decoded_url = unquote(url)
        readable_url = self._shorten(decoded_url, url_length)
        self._log(
            level=LogLevel.SUCCESS if success else LogLevel.ERROR,
            message="{url} | {status} | ⏱: {timing:.2f}s",
            tag=tag,
            params={
                "url": readable_url,
                "status": "✓" if success else "✗",
                "timing": timing,
            },
            colors={
                "status": LogColor.SUCCESS if success else LogColor.ERROR,
                "timing": LogColor.WARNING,
            },
        )
        if self.log_file:
            status = "✓" if success else "✗"
            self.loguru.debug(f"[{tag}] {url} | {status} | ⏱: {timing:.2f}s")

    def error_status(
        self, url: str, error: str, tag: str = "ERROR", url_length: int = 50
    ):
        """
        Convenience method for logging error status.

        Args:
            url: The URL being processed
            error: Error message
            tag: Tag for the message
            url_length: Maximum length for URL in log
        """
        decoded_url = unquote(url)
        readable_url = self._shorten(decoded_url, url_length)
        self._log(
            level=LogLevel.ERROR,
            message="{url} | Error: {error}",
            tag=tag,
            params={"url": readable_url, "error": error},
        )
        if self.log_file:
            self.loguru.error(f"\n[URL] {url}\n[ErrorMessage] {error}")
