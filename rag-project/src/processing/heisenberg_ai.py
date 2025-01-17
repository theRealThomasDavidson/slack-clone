"""
Walter White (Heisenberg) AI assistant.
Responds in character as the brilliant but prideful chemistry teacher turned drug kingpin.
"""
from .character_ai import CharacterAI

class HeisenbergAI(CharacterAI):
    def __init__(self):
        personality_traits = """
- Highly intelligent and prideful
- Manipulative and calculating
- Obsessed with power and control
- Uses scientific/chemistry terminology
- Often justifies actions as "for the family"
- Can be condescending and egotistical
- Prone to angry outbursts when challenged
- Strategic thinker who plans ahead
"""
        super().__init__(
            username="heisenberg",
            password="iamthedanger",
            character_name="Walter White",
            personality_traits=personality_traits
        )

def main():
    """Run the Heisenberg AI bot for one pass."""
    print("Starting Heisenberg AI check...")
    try:
        heisenberg = HeisenbergAI()
        heisenberg.check_and_respond()
        print("Check complete.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 