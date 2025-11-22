import pytest
from solution import PrefixTrie


def test_basic_insert_search():
    """Insert and search for words."""
    trie = PrefixTrie()
    trie.insert("apple")
    assert trie.search("apple") == True
    assert trie.search("app") == False


def test_prefix_count():
    """Count words with given prefix."""
    trie = PrefixTrie()
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")

    assert trie.starts_with("app") == 3
    assert trie.starts_with("appl") == 2
    assert trie.starts_with("b") == 0


def test_duplicate_insertion():
    """Duplicates are counted separately."""
    trie = PrefixTrie()
    trie.insert("apple")
    trie.insert("apple")
    trie.insert("apple")

    assert trie.starts_with("apple") == 3
    assert trie.search("apple") == True


def test_delete_word():
    """Delete removes one instance."""
    trie = PrefixTrie()
    trie.insert("apple")
    trie.insert("apple")

    assert trie.delete("apple") == True
    assert trie.search("apple") == True  # Still one left
    assert trie.starts_with("apple") == 1


def test_delete_last_instance():
    """Delete last instance removes word."""
    trie = PrefixTrie()
    trie.insert("apple")
    trie.delete("apple")

    assert trie.search("apple") == False
    assert trie.starts_with("apple") == 0


def test_delete_nonexistent():
    """Delete non-existent word returns False."""
    trie = PrefixTrie()
    trie.insert("apple")

    assert trie.delete("banana") == False
    assert trie.delete("app") == False  # Prefix exists but not as word


def test_prefix_only():
    """Prefix exists but not as complete word."""
    trie = PrefixTrie()
    trie.insert("application")

    assert trie.search("app") == False
    assert trie.starts_with("app") == 1


def test_empty_string():
    """Handle empty string."""
    trie = PrefixTrie()
    trie.insert("")

    assert trie.search("") == True
    assert trie.starts_with("") >= 1


def test_single_character():
    """Single character words."""
    trie = PrefixTrie()
    trie.insert("a")
    trie.insert("b")

    assert trie.search("a") == True
    assert trie.starts_with("a") == 1


def test_overlapping_words():
    """Words that are prefixes of each other."""
    trie = PrefixTrie()
    trie.insert("car")
    trie.insert("card")
    trie.insert("cards")
    trie.insert("cart")

    assert trie.starts_with("car") == 4
    assert trie.starts_with("card") == 2
    assert trie.search("car") == True
    assert trie.search("card") == True


def test_no_common_prefix():
    """Words with no common prefix."""
    trie = PrefixTrie()
    trie.insert("apple")
    trie.insert("banana")
    trie.insert("cherry")

    assert trie.starts_with("a") == 1
    assert trie.starts_with("b") == 1
    assert trie.starts_with("c") == 1
    assert trie.starts_with("d") == 0


def test_delete_affects_count():
    """Delete updates prefix counts correctly."""
    trie = PrefixTrie()
    trie.insert("application")
    trie.insert("apple")
    trie.insert("app")

    assert trie.starts_with("app") == 3
    trie.delete("application")
    assert trie.starts_with("app") == 2
    assert trie.starts_with("appli") == 0


def test_large_trie():
    """Many words with common prefixes."""
    trie = PrefixTrie()
    words = [f"word{i}" for i in range(100)]
    for w in words:
        trie.insert(w)

    assert trie.starts_with("word") == 100
    assert trie.starts_with("word1") >= 11  # word1, word10-19
