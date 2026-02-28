#!/usr/bin/env python3
"""
Simple wrapper for OpenClaw to call the game.
Usage: python3 game.py <chat_id> <message>
"""

import sys
import os

# Add the game directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import process_message

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 game.py <chat_id> <message>")
        print("Example: python3 game.py 73182477 /startgame")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    message = sys.argv[2]
    
    response = process_message(chat_id, message)
    print(response)
