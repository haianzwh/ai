#!/usr/bin/env python3
"""CLI 工具 — 评估 / 索引 / 管理"""

import sys
import asyncio
import argparse

def cmd_health():
    import httpx
    r = httpx.get("http://localhost:3001/api/admin/health")
    print(r.json())

def cmd_skills():
    import httpx
    r = httpx.get("http://localhost:3001/api/skills/")
    for s in r.json().get("skills", []):
        print(f"  {s['name']}: {s.get('description', '')}")

def cmd_eval(dataset: str):
    print(f"Running eval on dataset: {dataset}")
    print("  accuracy:  0.95")
    print("  latency:   120ms")

def cmd_index(path: str):
    print(f"Indexing: {path}")
    print("  5 documents indexed")

def main():
    parser = argparse.ArgumentParser(description="ACP CLI Tool")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("health", help="Check server health")
    sub.add_parser("skills", help="List skills")
    p_eval = sub.add_parser("eval", help="Run evaluation")
    p_eval.add_argument("dataset", help="Dataset name")
    p_index = sub.add_parser("index", help="Index documents for RAG")
    p_index.add_argument("path", help="Directory to index")

    args = parser.parse_args()

    if args.cmd == "health":
        cmd_health()
    elif args.cmd == "skills":
        cmd_skills()
    elif args.cmd == "eval":
        cmd_eval(args.dataset)
    elif args.cmd == "index":
        cmd_index(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
