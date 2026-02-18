"""
Tests for text chunking utilities.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the chunker, if it exists
try:
    from utils.chunker import chunk_text, chunk_by_paragraphs, chunk_by_sentences
    CHUNKER_AVAILABLE = True
except ImportError:
    CHUNKER_AVAILABLE = False


class TestChunking:
    """Test cases for text chunking utilities."""
    
    def test_chunk_text_available(self):
        """Test that chunker module is available."""
        assert CHUNKER_AVAILABLE, "Chunker module not available"
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        result = chunk_text("")
        assert result == []
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_short_text(self):
        """Test chunking short text."""
        text = "This is a short text."
        result = chunk_text(text)
        assert isinstance(result, list)
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_long_text(self):
        """Test chunking long text."""
        text = "This is a longer text. " * 100
        result = chunk_text(text, chunk_size=100)
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_by_paragraphs(self):
        """Test chunking by paragraphs."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = chunk_by_paragraphs(text)
        assert len(result) >= 3
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_by_sentences(self):
        """Test chunking by sentences."""
        text = "This is sentence one. This is sentence two. This is sentence three."
        result = chunk_by_sentences(text, chunks=2)
        assert isinstance(result, list)
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_with_overlap(self):
        """Test chunking with overlap."""
        text = "This is a test text for chunking. " * 50
        result = chunk_text(text, chunk_size=50, overlap=10)
        assert isinstance(result, list)
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_preserves_content(self):
        """Test that chunking preserves content."""
        text = "This is important content that should be preserved."
        result = chunk_text(text)
        
        # Join all chunks and check if original text is contained
        combined = " ".join(result)
        assert "important" in combined.lower()


class TestChunkingEdgeCases:
    """Test edge cases for chunking."""
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_none_text(self):
        """Test chunking None text."""
        result = chunk_text(None)
        assert result == []
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_whitespace_only(self):
        """Test chunking whitespace-only text."""
        result = chunk_text("   \n\n   ")
        assert isinstance(result, list)
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_special_characters(self):
        """Test chunking text with special characters."""
        text = "Contract #12345! @special #hashtag $100"
        result = chunk_text(text)
        assert isinstance(result, list)
    
    @pytest.mark.skipif(not CHUNKER_AVAILABLE, reason="Chunker not available")
    def test_chunk_unicode_text(self):
        """Test chunking unicode text."""
        text = "This is a test with unicode: émojis 🚀 and ümläüts"
        result = chunk_text(text)
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
