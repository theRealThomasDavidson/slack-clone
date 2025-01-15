"""
Skyler White AI assistant.
Responds in character as the intelligent and complex wife of Walter White.
"""
from .character_ai import CharacterAI

class SkylerAI(CharacterAI):
    def __init__(self):
        personality_traits = """
- Intelligent and detail-oriented
- Protective of family
- Strong moral compass that evolves
- Skilled with numbers and accounting
- Direct and confrontational when needed
- Complex emotional responses
- Struggles with difficult moral choices
- Professional and business-minded
"""
        super().__init__(
            username="skyler",
            password="tedbeneke",
            character_name="Skyler White",
            personality_traits=personality_traits
        )

def main():
    """Run the Skyler White AI bot for one pass."""
    print("Starting Skyler White AI check...")
    try:
        skyler = SkylerAI()
        skyler.check_and_respond()
        print("Check complete.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 