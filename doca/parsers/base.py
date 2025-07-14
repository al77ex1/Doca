"""
Base parser class for Doca
Defines the interface for all document parsers
"""

from abc import ABC, abstractmethod
from typing import List


class BaseParser(ABC):
    """
    Abstract base class for document parsers
    All specific file format parsers should inherit from this class
    """
    
    @abstractmethod
    def parse(self, content: str) -> str:
        """
        Parse document content into plain text for embedding
        
        Args:
            content: Raw document content as string
            
        Returns:
            Processed plain text ready for embedding
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get list of file extensions supported by this parser
        
        Returns:
            List of supported file extensions (without dot)
        """
        pass
