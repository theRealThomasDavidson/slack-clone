import sys
import os
import bcrypt
import json
from uuid import UUID
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import Base
from api.models.tables.user import User
from api.models.tables.channel import Channel
from api.models.tables.message import Message

# Custom JSON encoder to handle UUID objects
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# Database connection with retry logic
def get_db_connection(max_retries=5):
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"
    for i in range(max_retries):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            engine.connect()
            return engine
        except Exception as e:
            if i == max_retries - 1:
                raise Exception(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
            print(f"Database connection attempt {i + 1} failed, retrying...")
            import time
            time.sleep(2)

engine = get_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_test_data():
    db = SessionLocal()
    try:
        # Create system user first
        system_user = User(
            username="system",
            email="system@chat.local",
            hashed_password=get_password_hash("systempassword123"),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(system_user)
        db.flush()

        # Create Breaking Bad characters as users
        test_users = [
            {"username": "heisenberg", "email": "walter.white@graymatter.com", "password": "iamthedanger"},
            {"username": "pinkman", "email": "jesse@yo.com", "password": "sciencebitch"},
            {"username": "saulgoodman", "email": "saul@bettercallsaul.com", "password": "itssallgoodman"},
            {"username": "gus", "email": "gus@lospolloshermanos.com", "password": "boxcutter"},
            {"username": "hank", "email": "hank.schrader@dea.gov", "password": "minerals"},
            {"username": "skyler", "email": "skyler.white@gmail.com", "password": "tedbeneke"}
        ]

        users = {"system": system_user}  # Add system user to users dict
        for user_data in test_users:
            try:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                db.flush()
                users[user.username] = user
            except Exception as e:
                print(f"Error creating user {user_data['username']}: {str(e)}")
                raise

        # Create themed channels
        channels = [
            {"name": "los-pollos", "description": "Los Pollos Hermanos Employee Chat", "is_private": False},
            {"name": "dea-office", "description": "DEA Albuquerque Office", "is_private": False},
            {"name": "rv-lab", "description": "Mobile Lab Discussion", "is_private": True},
            {"name": "sauls-office", "description": "Legal Consultation Room", "is_private": False},
            {"name": "general", "description": "Albuquerque General Chat", "is_private": False}
        ]

        channel_objects = {}
        for channel_data in channels:
            try:
                channel = Channel(
                    name=channel_data["name"],
                    description=channel_data["description"],
                    is_private=channel_data["is_private"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                # Add all users (except system) to public channels, but only specific users to private ones
                if not channel_data["is_private"]:
                    channel.members.extend([u for u in users.values() if u.username != "system"])
                elif channel_data["name"] == "rv-lab":
                    channel.members.extend([users["heisenberg"], users["pinkman"]])
                
                db.add(channel)
                db.flush()
                channel_objects[channel.name] = channel

                # Add system welcome message to each channel
                welcome_msg = Message(
                    channel_id=channel.id,
                    user_id=system_user.id,
                    content=f"Welcome to {channel.name}! {channel.description}",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(welcome_msg)

            except Exception as e:
                print(f"Error creating channel {channel_data['name']}: {str(e)}")
                raise

        # Add iconic messages
        test_messages = [
            # General channel (20+ messages)
            {"channel": "general", "user": "heisenberg", "content": "I am the one who knocks!"},
            {"channel": "general", "user": "pinkman", "content": "Yeah, science! Yeah, Mr. White!"},
            {"channel": "general", "user": "skyler", "content": "Someone has to protect this family from the man who protects this family."},
            {"channel": "general", "user": "heisenberg", "content": "Say my name."},
            {"channel": "general", "user": "pinkman", "content": "You're Heisenberg..."},
            {"channel": "general", "user": "heisenberg", "content": "You're goddamn right!"},
            {"channel": "general", "user": "saulgoodman", "content": "If you're committed enough, you can make any story work."},
            {"channel": "general", "user": "gus", "content": "I hide in plain sight, same as you."},
            {"channel": "general", "user": "hank", "content": "My name is ASAC Schrader, and you can go **** yourself."},
            {"channel": "general", "user": "skyler", "content": "I'm waiting for the cancer to come back."},
            {"channel": "general", "user": "pinkman", "content": "He can't keep getting away with it!"},
            {"channel": "general", "user": "heisenberg", "content": "We're done when I say we're done."},
            {"channel": "general", "user": "skyler", "content": "I learned from the best."},
            {"channel": "general", "user": "gus", "content": "Never make the same mistake twice."},
            {"channel": "general", "user": "saulgoodman", "content": "Let's just say I know a guy who knows a guy."},
            {"channel": "general", "user": "pinkman", "content": "Magnets, yo!"},
            {"channel": "general", "user": "heisenberg", "content": "I did it for me. I liked it. I was good at it."},
            {"channel": "general", "user": "skyler", "content": "Have an A1 day!"},
            {"channel": "general", "user": "gus", "content": "Don't make me wait."},
            {"channel": "general", "user": "pinkman", "content": "This is my own private domicile and I will not be harassed... bitch!"},

            # Los Pollos channel (20+ messages)
            {"channel": "los-pollos", "user": "gus", "content": "Welcome to Los Pollos Hermanos, where something delicious is always cooking."},
            {"channel": "los-pollos", "user": "gus", "content": "A man provides for his family."},
            {"channel": "los-pollos", "user": "gus", "content": "The chicken brothers is now open for business!"},
            {"channel": "los-pollos", "user": "gus", "content": "Please remember our employee guidelines."},
            {"channel": "los-pollos", "user": "gus", "content": "Customer satisfaction is our priority."},
            {"channel": "los-pollos", "user": "gus", "content": "Today's special: Extra crispy chicken."},
            {"channel": "los-pollos", "user": "gus", "content": "Remember to keep the kitchen spotless."},
            {"channel": "los-pollos", "user": "gus", "content": "Employee of the month nominations are open."},
            {"channel": "los-pollos", "user": "gus", "content": "New delivery schedule posted in break room."},
            {"channel": "los-pollos", "user": "gus", "content": "Mandatory staff meeting next Tuesday."},
            {"channel": "los-pollos", "user": "gus", "content": "Don't forget to smile!"},
            {"channel": "los-pollos", "user": "gus", "content": "Quality is our recipe."},
            {"channel": "los-pollos", "user": "gus", "content": "New sauce recipe implementation next week."},
            {"channel": "los-pollos", "user": "gus", "content": "Remember our commitment to excellence."},
            {"channel": "los-pollos", "user": "gus", "content": "Health inspection next month - be prepared."},
            {"channel": "los-pollos", "user": "gus", "content": "Employee discounts now available."},
            {"channel": "los-pollos", "user": "gus", "content": "Keep the front counter clean at all times."},
            {"channel": "los-pollos", "user": "gus", "content": "New uniforms arriving next week."},
            {"channel": "los-pollos", "user": "gus", "content": "Remember to check the fryer temperature."},
            {"channel": "los-pollos", "user": "gus", "content": "Customer feedback forms are important."},

            # DEA office channel (15+ messages)
            {"channel": "dea-office", "user": "hank", "content": "They're not rocks, they're minerals, Marie!"},
            {"channel": "dea-office", "user": "hank", "content": "Follow the money trail, folks!"},
            {"channel": "dea-office", "user": "hank", "content": "Blue meth spotted in the southwest region."},
            {"channel": "dea-office", "user": "hank", "content": "New case files on my desk by Monday."},
            {"channel": "dea-office", "user": "hank", "content": "Meeting with El Paso office tomorrow."},
            {"channel": "dea-office", "user": "hank", "content": "Someone's been cooking some serious crystal."},
            {"channel": "dea-office", "user": "hank", "content": "Surveillance photos needed for the Salamanca case."},
            {"channel": "dea-office", "user": "hank", "content": "Drug bust scheduled for next week."},
            {"channel": "dea-office", "user": "hank", "content": "New evidence in the Heisenberg case."},
            {"channel": "dea-office", "user": "hank", "content": "Mandatory training session next Thursday."},
            {"channel": "dea-office", "user": "hank", "content": "Keep an eye on suspicious chicken farms."},
            {"channel": "dea-office", "user": "hank", "content": "Update your incident reports, people!"},
            {"channel": "dea-office", "user": "hank", "content": "Cartel activity increasing near the border."},
            {"channel": "dea-office", "user": "hank", "content": "All hands meeting at 3 PM."},
            {"channel": "dea-office", "user": "hank", "content": "Jesus Christ, Marie!"},

            # RV lab channel (10+ messages)
            {"channel": "rv-lab", "user": "pinkman", "content": "Yo, this RV is like, the bomb, yo"},
            {"channel": "rv-lab", "user": "heisenberg", "content": "Jesse, we need to cook."},
            {"channel": "rv-lab", "user": "pinkman", "content": "The batch is ready, Mr. White!"},
            {"channel": "rv-lab", "user": "heisenberg", "content": "The methylamine is running low."},
            {"channel": "rv-lab", "user": "pinkman", "content": "I applied myself, just like you said!"},
            {"channel": "rv-lab", "user": "heisenberg", "content": "Check the temperature, Jesse!"},
            {"channel": "rv-lab", "user": "pinkman", "content": "This is art, Mr. White. Yeah!"},
            {"channel": "rv-lab", "user": "heisenberg", "content": "The formula must be precise."},
            {"channel": "rv-lab", "user": "pinkman", "content": "Wire! Copper wire!"},
            {"channel": "rv-lab", "user": "heisenberg", "content": "We need to be careful with the measurements."},

            # Saul's office channel (10+ messages)
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Better Call Saul! Did you know that you have rights? Constitution says you do!"},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "I know a guy who knows a guy... who knows another guy."},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Let's keep this between us counselor-client privilege."},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Need a will? Call McGill!"},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Appointments available all week."},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Remember, I'm a criminal lawyer... a CRIMINAL lawyer."},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Free consultation for new clients!"},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Don't drink and drive, but if you do, call me!"},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "Huell, we need more security at the front desk."},
            {"channel": "sauls-office", "user": "saulgoodman", "content": "It's all good, man!"}
        ]

        for msg_data in test_messages:
            try:
                message = Message(
                    channel_id=channel_objects[msg_data["channel"]].id,
                    user_id=users[msg_data["user"]].id,
                    content=msg_data["content"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(message)
            except Exception as e:
                print(f"Error creating message in channel {msg_data['channel']}: {str(e)}")
                raise

        db.commit()
        print("Breaking Bad themed test data created successfully!")

    except Exception as e:
        print(f"Error creating test data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        print("Creating Breaking Bad test data...")
        create_test_data()
        print("Done!")
    except Exception as e:
        print(f"Failed to create test data: {str(e)}")
        sys.exit(1) 