"""
C4A-Script: A domain-specific language for web automation in Crawl4AI
"""

from .compile import C4ACompiler, compile, validate, compile_file
from .result import (
    CompilationResult, 
    ValidationResult, 
    ErrorDetail, 
    WarningDetail,
    ErrorType, 
    Severity, 
    Suggestion
)

__all__ = [
    # Main compiler
    "C4ACompiler",
    
    # Convenience functions
    "compile",
    "validate", 
    "compile_file",
    
    # Result types
    "CompilationResult",
    "ValidationResult",
    "ErrorDetail",
    "WarningDetail",
    
    # Enums
    "ErrorType",
    "Severity",
    "Suggestion"
]