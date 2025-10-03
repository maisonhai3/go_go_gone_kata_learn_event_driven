#!/usr/bin/env python3
"""
Demo: Replay events from Redis Streams.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run
if __name__ == "__main__":
    # Execute replay demo as if it were the main script
    import runpy
    runpy.run_module('src.demos.example_replay', run_name='__main__')
