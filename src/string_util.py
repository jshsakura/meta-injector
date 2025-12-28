"""String utility functions for WiiVC Injector."""
import unicodedata


def remove_diacritics(text: str) -> str:
    """
    Remove diacritics (accents) from text.

    Args:
        text: Input string with possible diacritics

    Returns:
        String with diacritics removed
    """
    normalized = unicodedata.normalize('NFD', text)
    result = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'
    )
    return unicodedata.normalize('NFC', result)


def remove_special_chars(text: str) -> str:
    """
    Remove special characters and non-ASCII characters from text.

    Args:
        text: Input string

    Returns:
        String with only ASCII characters (< 128)
    """
    if not text:
        return text

    # First remove diacritics
    text = remove_diacritics(text)

    # Keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)


def replace_at(text: str, index: int, new_char: str) -> str:
    """
    Replace character at specific index.

    Args:
        text: Input string
        index: Position to replace
        new_char: New character

    Returns:
        String with character replaced

    Raises:
        ValueError: If text is None
        IndexError: If index is out of range
    """
    if text is None:
        raise ValueError("Input text cannot be None")

    chars = list(text)
    chars[index] = new_char
    return ''.join(chars)
