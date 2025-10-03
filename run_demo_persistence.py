#!/usr/bin/env python3
"""
Demo: Show persisted events in Redis.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run
if __name__ == "__main__":
    # Execute demo as if it were the main script
    import runpy
    runpy.run_module('src.demos.demo_persistence', run_name='__main__')
