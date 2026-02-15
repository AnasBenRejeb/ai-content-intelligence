#!/bin/bash
echo "Installing Multi-Agent News Intelligence System..."
echo

pip install requests rapidfuzz keybert langdetect sentence-transformers
pip install pydantic pydantic-settings aiohttp tenacity rich

echo
echo "Installation complete!"
echo
echo "To run the system:"
echo "  python run.py"
echo
echo "To run the demo:"
echo "  python demo.py"
