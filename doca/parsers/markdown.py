"""
Markdown parser for Doca
Converts markdown documents to plain text for embedding
"""

import markdown
from typing import List

from .base import BaseParser


class MarkdownParser(BaseParser):
    """Parser for Markdown documents"""
    
    def parse(self, content: str) -> str:
        """
        Parse markdown content into plain text
        
        Args:
            content: Raw markdown content
            
        Returns:
            Plain text extracted from markdown
        """
        # Convert markdown to HTML
        html = markdown.markdown(content)
        
        # Simple HTML to text conversion
        # Remove HTML tags
        text = html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        for tag in ["<p>", "</p>", "<h1>", "</h1>", "<h2>", "</h2>", "<h3>", "</h3>", 
                   "<h4>", "</h4>", "<h5>", "</h5>", "<h6>", "</h6>", "<ul>", "</ul>", 
                   "<li>", "</li>", "<strong>", "</strong>", "<em>", "</em>"]:
            text = text.replace(tag, " ")
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        return text
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get list of file extensions supported by this parser
        
        Returns:
            List of supported file extensions (without dot)
        """
        return ["md", "markdown"]
