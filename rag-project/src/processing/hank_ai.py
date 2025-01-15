"""
Hank Schrader AI assistant.
Responds in character as the tough but good-hearted DEA agent.
"""
from .character_ai import CharacterAI

class HankAI(CharacterAI):
    def __init__(self):
        personality_traits = """
- Tough and determined DEA agent
- Uses law enforcement terminology
- Passionate about his work
- Loves minerals (not rocks!)
- Macho exterior but caring inside
- Uses humor to lighten situations
- Strong sense of justice
- Dedicated to family and duty
"""
        super().__init__(
            username="hank",
            password="minerals",
            character_name="Hank Schrader",
            personality_traits=personality_traits
        )

def main():
    """Run the Hank Schrader AI bot for one pass."""
    print("Starting Hank Schrader AI check...")
    try:
        hank = HankAI()
        hank.check_and_respond()
        print("Check complete.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 