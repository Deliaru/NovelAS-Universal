"""
Token estimation for dynamic batch sizing.
Provides rough token counts based on character count heuristics.
"""


def estimate_tokens(text: str, model_family: str = "default") -> int:
    """
    Estimate token count for a text string.

    Uses character-based heuristics:
    - Chinese text: ~1.5 tokens per character
    - English text: ~0.75 tokens per word (~4 chars per token)
    - Mixed: weighted average

    Args:
        text: Input text.
        model_family: Model family hint ("openai", "anthropic", "gemini", "default").

    Returns:
        Estimated token count.
    """
    import re

    # Count CJK characters
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))
    # Count remaining (Latin, numbers, punctuation)
    non_cjk_chars = len(text) - cjk_chars

    # CJK: roughly 1.5 tokens per character (most models)
    # Latin: roughly 1 token per 4 characters
    cjk_tokens = int(cjk_chars * 1.5)
    latin_tokens = int(non_cjk_chars / 4)

    total = cjk_tokens + latin_tokens

    # Model-specific adjustments
    if model_family == "anthropic":
        total = int(total * 1.1)  # Claude tends to tokenize CJK more finely
    elif model_family == "gemini":
        total = int(total * 0.95)  # Gemini tokenizer is slightly more efficient

    return max(1, total)


def estimate_max_chapters(
    char_budget: int,
    avg_chapter_chars: int = 3000,
    model_family: str = "default",
) -> int:
    """
    Estimate how many chapters fit within a token budget.

    Args:
        char_budget: Maximum characters to process.
        avg_chapter_chars: Average characters per chapter.
        model_family: Model family for token estimation.

    Returns:
        Estimated number of chapters.
    """
    if avg_chapter_chars <= 0:
        return 1
    return max(1, char_budget // avg_chapter_chars)
