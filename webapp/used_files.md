# Application File Structure and Dependencies

## External Dependencies
### Already Found
1. FastAPI Related:
   - `fastapi`
   - `fastapi.middleware.cors`
   - `fastapi.UploadFile`
   - `fastapi.File`
   - `fastapi.Form`
   - `starlette.responses`
2. Database Related:
   - `sqlalchemy`
   - `sqlalchemy.ext.asyncio`
   - `sqlalchemy.orm`
   - `sqlalchemy.dialects.postgresql`
3. System/Deployment:
   - `python:3.11-slim` (Docker base image)
   - `postgresql-client`
   - `netcat-traditional`
4. Python Standard Library:
   - `os`
   - `shutil`
   - `uuid`
   - `logging`
   - `pathlib`
   - `typing`
   - `re`
   - `datetime`
5. Data Validation:
   - `pydantic`
   - `pydantic.BaseModel`
   - `pydantic.Field`
   - `pydantic.field_validator`

## API Backend

### Entry Point Chain
1. `api/Dockerfile`
   - Purpose: Container configuration
   - Key Dependencies:
     - python:3.11-slim
     - postgresql-client
     - netcat-traditional

2. `api/scripts/start.sh`
   - Purpose: Application startup script
   - Executes: `scripts/setup.py`

3. `api/scripts/setup.py`
   - Purpose: Database and application initialization
   - Key Imports:
     - `api.database` (Base, engine)
     - `api.main:app` (FastAPI application)
   - Functions:
     - `wait_for_db()`
     - `create_database()`
     - `main()`

4. `api/api/main.py`
   - Purpose: FastAPI application setup
   - Key Imports:
     - `fastapi`
     - `fastapi.middleware.cors`
     - Route modules:
       - `api.routes.auth`
       - `api.routes.channel`
       - `api.routes.messages`
       - `api.routes.users`
       - `api.routes.files`

### Already Analyzed Routes and Services
1. Routes:
   - `api/api/routes/auth.py`
     - Imports:
       - `fastapi`
       - `sqlalchemy`
       - `../database`
       - `../models/user`
       - `../models/tables/user`
       - `../services/auth`

   - `api/api/routes/channel.py`
     - Imports:
       - `fastapi`
       - `sqlalchemy`
       - `../database`
       - `../models/channel`
       - `../models/tables/user`
       - `../models/tables/message`
       - `../models/tables/reaction`
       - `../services/channel`
       - `../services/auth`

   - `api/api/routes/messages.py`
     - Imports:
       - Standard library: `os`, `shutil`, `uuid`, `logging`, `pathlib`, `re`
       - FastAPI: `APIRouter`, `Depends`, `HTTPException`, `status`, `UploadFile`, `File`, `Form`
       - SQLAlchemy: `AsyncSession`, `select`, `text`, `joinedload`
       - Local:
         - `../database`
         - `../models/tables/user`
         - `../models/tables/message`
         - `../models/tables/reaction`
         - `../models/tables/file`
         - `../models/tables/channel`
         - `../models/message`
         - `../routes/auth`

   - `api/api/routes/users.py`
     - Imports:
       - FastAPI: `APIRouter`, `Depends`, `HTTPException`, `status`
       - SQLAlchemy: `AsyncSession`, `select`
       - Pydantic: `BaseModel`
       - Local:
         - `../database`
         - `../models/user`
         - `../models/tables/user`
         - `../services/auth`
         - `./auth`

   - `api/api/routes/files.py`
     - Imports:
       - Standard library: `os`, `shutil`, `uuid`, `logging`, `pathlib`
       - FastAPI: `APIRouter`, `Depends`, `HTTPException`, `status`, `UploadFile`, `File`, `Form`
       - Starlette: `FileResponse`
       - SQLAlchemy: `AsyncSession`
       - Local:
         - `../database`
         - `../models/tables/user`
         - `../models/tables/file`
         - `../models/file`
         - `../models/tables/message`
         - `../routes/auth`

2. Services:
   - `api/api/services/auth.py`
   - `api/api/services/channel.py`

### New Routes To Analyze
1. `api/api/routes/files.py`

### Already Analyzed Models
1. `api/api/models/user.py`
   - Purpose: Pydantic models for user data validation
   - Models:
     - `UserBase`: Base model with username and email
     - `UserCreate`: Extends base with password
     - `UserUpdate`: Optional fields for updates
     - `User`: Response model with additional fields
   - Imports:
     - Standard library: `datetime`, `typing`, `re`
     - Pydantic: `BaseModel`, `Field`, `field_validator`

2. `api/api/models/channel.py`
   - Purpose: Pydantic models for channel data validation
   - Models:
     - `ChannelBase`: Base model with name, description, and privacy flag
     - `ChannelCreate`: Creation model extending base
     - `Channel`: Response model with additional fields
   - Imports:
     - Standard library: `datetime`, `typing`
     - Pydantic: `BaseModel`, `Field`

3. `api/api/models/tables/user.py`
   - Purpose: SQLAlchemy model for user database table
   - Fields:
     - Basic: id, username, email, hashed_password, is_active
     - Timestamps: created_at, updated_at
   - Relationships:
     - messages (Message)
     - channels (Channel through channel_members)
     - reactions (Reaction)
     - files (File)
   - Imports:
     - Standard library: `datetime`
     - SQLAlchemy: `Column`, `Integer`, `String`, `DateTime`, `Boolean`, `relationship`
     - Local: `...database` (Base)

4. `api/api/models/tables/message.py`
   - Purpose: SQLAlchemy model for message database table
   - Fields:
     - Basic: id, content, user_id, channel_id, parent_id
     - Timestamps: created_at, updated_at
   - Relationships:
     - user (User)
     - channel (Channel)
     - reactions (Reaction)
     - file (File, one-to-one)
     - parent_message (Message self-reference)
     - replies (Message self-reference)
   - Imports:
     - Standard library: `datetime`
     - SQLAlchemy: `Column`, `DateTime`, `Integer`, `String`, `ForeignKey`, `Text`, `relationship`
     - Local: `...database` (Base)

5. `api/api/models/tables/reaction.py`
   - Purpose: SQLAlchemy model for reaction database table
   - Fields:
     - Basic: id, emoji, user_id, message_id
     - Timestamps: created_at
   - Relationships:
     - user (User)
     - message (Message)
   - Constraints:
     - Unique: (user_id, message_id, emoji)
   - Imports:
     - Standard library: `datetime`
     - SQLAlchemy: `Column`, `DateTime`, `Integer`, `String`, `ForeignKey`, `UniqueConstraint`, `relationship`
     - Local: `...database` (Base)

6. `api/api/models/tables/file.py`
   - Purpose: SQLAlchemy model for file database table
   - Fields:
     - Basic: id (UUID), filename, filepath, content_type, size, user_id, message_id
     - Timestamps: created_at
   - Relationships:
     - message (Message)
   - Imports:
     - Standard library: `datetime`, `uuid`
     - SQLAlchemy: `Column`, `DateTime`, `Integer`, `String`, `ForeignKey`, `relationship`
     - PostgreSQL specific: `sqlalchemy.dialects.postgresql.UUID`
     - Local: `...database` (Base)

### Models To Analyze
1. `api/api/models/message.py`
2. `api/api/models/file.py`

### Core Components To Analyze
1. `api/api/database.py`

## Frontend (Referenced but not primary focus)
- Entry: `frontend/src/main.tsx`
- Key Components:
  - `frontend/src/components/chat/UserList.tsx`
  - `frontend/src/components/chat/ChannelList.tsx`
  - `frontend/src/pages/Chat.tsx` 