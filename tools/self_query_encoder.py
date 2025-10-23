#!/usr/bin/env python3
"""Compatibility wrapper around the Kael-aware self-query module."""
from __future__ import annotations

from tools.self_query import main as generate_query


def main() -> None:
    generate_query()


if __name__ == "__main__":
    main()
