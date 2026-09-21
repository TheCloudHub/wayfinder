#!/usr/bin/env python3
"""Ingest the knowledge base into the vector store.

Usage:
    python scripts/ingest_docs.py                 # ingest data/knowledge_base
    python scripts/ingest_docs.py --dir some/dir   # ingest a custom directory
    python scripts/ingest_docs.py --url https://... https://...
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.ingest import ingest_directory, ingest_urls  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest docs into the RAG vector store")
    parser.add_argument("--dir", help="Directory of docs to ingest")
    parser.add_argument("--url", nargs="+", help="One or more documentation URLs")
    parser.add_argument("--category", default="web", help="Category tag for URL ingestion")
    args = parser.parse_args()

    if args.url:
        result = ingest_urls(args.url, category=args.category)
    else:
        result = ingest_directory(args.dir)

    print(result)


if __name__ == "__main__":
    main()
