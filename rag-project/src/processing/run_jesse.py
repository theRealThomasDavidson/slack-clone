"""
Single-run script for Jesse Pinkman AI.
Checks messages once and responds where appropriate.
"""
from .jesse_ai import JesseAI

def main():
    """Run Jesse AI once."""
    print("Starting Jesse Pinkman AI check...")
    try:
        jesse = JesseAI()
        jesse.check_and_respond()
        print("Check complete, yo!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 