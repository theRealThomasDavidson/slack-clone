
## Our Application Modules
- [ ] api.core.config
  - [ ] settings
- [ ] api.core.database
  - [ ] Base
  - [ ] SessionLocal
  - [ ] get_db
- [ ] api.core.security
  - [ ] verify_password
  - [ ] get_password_hash
  - [ ] create_access_token
- [ ] api.models.user
  - [ ] User
  - [ ] UserCreate
- [ ] api.models.auth
  - [ ] LoginRequest
  - [ ] RegisterRequest
  - [ ] Token
  - [ ] TokenData
- [ ] api.services.auth
  - [ ] AuthService
- [ ] api.routes
  - [ ] auth_router
  - [ ] users_router
  - [ ] channels_router
  - [ ] chat_router

## Requirements Status
All these imports require the following packages in requirements.txt:
- [ ] fastapi
- [ ] uvicorn
- [ ] sqlalchemy
- [ ] pydantic
- [ ] python-jose[cryptography]
- [ ] passlib[bcrypt]
- [ ] python-multipart
- [ ] email-validator
- [ ] psycopg2-binary 