class PrefixTrie:
    """
    Trie supporting word insertion, search, and prefix counting.

    Each node maintains:
    - children: dict mapping characters to child nodes
    - count: number of words passing through this node (for prefix counting)
    - end_count: number of words ending at this node (for handling duplicates)
    """

    def __init__(self):
        """Initialize empty trie."""
        self.children = {}
        self.count = 0      # Words passing through this node
        self.end_count = 0  # Words ending at this node

    def insert(self, word: str) -> None:
        """Insert word into trie."""
        node = self
        node.count += 1  # Root count for empty prefix
        for char in word:
            if char not in node.children:
                node.children[char] = PrefixTrie()
            node = node.children[char]
            node.count += 1
        node.end_count += 1

    def search(self, word: str) -> bool:
        """Return True if exact word exists."""
        node = self
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.end_count > 0

    def starts_with(self, prefix: str) -> int:
        """Return count of words starting with prefix."""
        node = self
        if prefix == "":
            return node.count
        for char in prefix:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.count

    def delete(self, word: str) -> bool:
        """
        Delete word from trie.
        Returns True if word existed, False otherwise.
        """
        # First check if the word exists
        node = self
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]

        if node.end_count == 0:
            return False

        # Word exists, decrement counts along the path
        node = self
        node.count -= 1
        for char in word:
            node = node.children[char]
            node.count -= 1
        node.end_count -= 1

        return True
