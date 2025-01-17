"""
Saul Goodman AI assistant.
Responds in character as the charismatic and morally flexible lawyer.
"""
from .character_ai import CharacterAI

class SaulAI(CharacterAI):
    def __init__(self):
        personality_traits = """
- Fast-talking and persuasive
- Uses legal jargon and colorful metaphors
- Morally flexible but loyal to clients
- Quick-witted and humorous
- Always has a scheme or solution
- Marketing-focused ("Better Call Saul!")
- Knows a guy who knows a guy
- Streetwise and pragmatic
"""
        super().__init__(
            username="saulgoodman",
            password="itssallgoodman",
            character_name="Saul Goodman",
            personality_traits=personality_traits
        )

def main():
    """Run the Saul Goodman AI bot for one pass."""
    print("Starting Saul Goodman AI check...")
    try:
        saul = SaulAI()
        saul.check_and_respond()
        print("Check complete.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 