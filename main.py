"""
Pump Narrative Scanner - Entry Point
A local Python research dashboard for monitoring newly created Solana meme tokens.
This tool is for research and screening only. It does not provide investment advice
and does not execute trades.
"""

import uvicorn
from config import APP_HOST, APP_PORT


def main():
    """Start the Pump Narrative Scanner dashboard."""
    print("Starting Pump Narrative Scanner...")
    print(f"Dashboard available at: http://{APP_HOST}:{APP_PORT}")
    uvicorn.run("web.app:app", host=APP_HOST, port=APP_PORT, reload=True)


if __name__ == "__main__":
    main()
