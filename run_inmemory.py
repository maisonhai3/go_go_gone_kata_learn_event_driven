#!/usr/bin/env python3
"""
Run the event-driven application with in-memory broker.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run
if __name__ == "__main__":
    # Execute main as if it were the main script
    import runpy
    runpy.run_module('src.main', run_name='__main__')
