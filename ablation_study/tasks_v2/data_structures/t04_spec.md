# Task: Trie with Prefix Count

Implement trie with efficient prefix counting.

**Class specification:**
```python
class PrefixTrie:
    """
    Trie supporting word insertion, search, and prefix counting.
    """

    def __init__(self):
        """Initialize empty trie."""
        pass

    def insert(self, word: str) -> None:
        """Insert word into trie."""
        pass

    def search(self, word: str) -> bool:
        """Return True if exact word exists."""
        pass

    def starts_with(self, prefix: str) -> int:
        """Return count of words starting with prefix."""
        pass

    def delete(self, word: str) -> bool:
        """
        Delete word from trie.
        Returns True if word existed, False otherwise.
        """
        pass
```

**Requirements:**
- All operations O(m) where m is word/prefix length
- starts_with() must use cached counts (not traverse all words)
- Support duplicate insertions (count each)
- delete() removes one instance
- Handle empty strings

**Example:**
```python
trie = PrefixTrie()
trie.insert("apple")
trie.insert("app")
trie.insert("apple")  # Duplicate

trie.search("app") == True
trie.search("appl") == False
trie.starts_with("app") == 3  # "apple" (x2) + "app" (x1)
trie.delete("apple")
trie.starts_with("app") == 2  # "apple" (x1) + "app" (x1)
```

**Difficulty:** Trie with count augmentation
