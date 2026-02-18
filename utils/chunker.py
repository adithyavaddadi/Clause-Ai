"""
Text chunking utilities for processing large documents.
"""

import re
from typing import List, Tuple


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    if not text:
        return []
    
    if chunk_size <= 0:
        chunk_size = 500
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 5)

    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end),
                text.rfind('\n', start, end)
            )
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = next_start
    
    return chunks


def chunk_by_paragraphs(text: str, min_paragraph_length: int = 10) -> List[str]:
    """
    Split text into paragraphs.
    
    Args:
        text: The text to split
        min_paragraph_length: Minimum length of a paragraph to include
        
    Returns:
        list: List of paragraphs
    """
    if not text:
        return []
    
    # Split by multiple newlines
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Filter out short paragraphs
    paragraphs = [p.strip() for p in paragraphs if len(p.strip()) >= min_paragraph_length]
    
    return paragraphs


def chunk_by_sentences(text: str, chunks: int = 5) -> List[str]:
    """
    Split text into roughly equal sentence chunks.
    
    Args:
        text: The text to split
        chunks: Number of chunks to create
        
    Returns:
        list: List of sentence chunks
    """
    if not text:
        return []
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return [text]
    
    if chunks <= 0:
        chunks = 1

    # Calculate sentences per chunk
    sentences_per_chunk = max(1, len(sentences) // chunks)
    
    result_chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        current_chunk.append(sentence)
        current_length += len(sentence)
        
        if len(current_chunk) >= sentences_per_chunk:
            result_chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    
    # Add remaining sentences
    if current_chunk:
        result_chunks.append(' '.join(current_chunk))
    
    return result_chunks


def chunk_by_tokens(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into token-based chunks (approximate).
    
    Note: This uses a rough approximation of 4 characters per token.
    
    Args:
        text: The text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap
        
    Returns:
        list: List of text chunks
    """
    # Rough token estimation: ~4 characters per token
    chars_per_token = 4
    chunk_size = max_tokens * chars_per_token
    overlap_chars = overlap * chars_per_token
    
    return chunk_text(text, chunk_size=chunk_size, overlap=overlap_chars)


def chunk_contract_sections(text: str) -> dict:
    """
    Attempt to identify and chunk contract sections.
    
    Args:
        text: The contract text
        
    Returns:
        dict: Dictionary of section_name -> section_text
    """
    sections = {}
    
    # Common contract section headers
    section_patterns = [
        r'(?i)^(RECITALS|PREAMBLE)\s*$',
        r'(?i)^(DEFINITIONS)\s*$',
        r'(?i)^(SERVICES?)\s*$',
        r'(?i)^(COMPENSATION|PAYMENT)\s*$',
        r'(?i)^(TERM|TERMINATION)\s*$',
        r'(?i)^(CONFIDENTIALITY)\s*$',
        r'(?i)^(LIABILITY|INDEMNIFICATION)\s*$',
        r'(?i)^(GOVERNING LAW|DISPUTES?)\s*$',
        r'(?i)^(GENERAL|MISCELLANEOUS)\s*$',
    ]
    
    lines = text.split('\n')
    current_section = "Introduction"
    current_content = []
    
    for line in lines:
        line = line.strip()
        
        # Check if line is a section header
        is_header = False
        for pattern in section_patterns:
            if re.match(pattern, line):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line
                current_content = []
                is_header = True
                break
        
        if not is_header and line:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


if __name__ == "__main__":
    # Test the chunking functions
    test_text = """
    This is the first sentence of our test document. It contains multiple sentences.
    Here is another sentence to work with. And yet another one for good measure.
    
    This is a new paragraph with more text. It also contains sentences.
    More text in this paragraph.
    
    A third paragraph for testing purposes. Testing chunking is important.
    """
    
    print("Testing chunk_text:")
    chunks = chunk_text(test_text, chunk_size=100, overlap=20)
    print(f"  Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  Chunk {i+1}: {chunk[:50]}...")
    
    print("\nTesting chunk_by_paragraphs:")
    paragraphs = chunk_by_paragraphs(test_text)
    print(f"  Created {len(paragraphs)} paragraphs")
    
    print("\nTesting chunk_by_sentences:")
    sentence_chunks = chunk_by_sentences(test_text, chunks=2)
    print(f"  Created {len(sentence_chunks)} sentence chunks")
