#!/usr/bin/env python
"""Simple runner script"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import main

if __name__ == "__main__":
    main()
