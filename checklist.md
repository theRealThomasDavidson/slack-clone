# API Testing Checklist

## Authentication Endpoints
- [x] POST `/api/v1/auth/register` - Register new user
- [x] POST `/api/v1/auth/login` - Login user
- [ ] POST `/api/v1/auth/logout` - Logout user
- [x] GET `/api/v1/auth/me` - Get current user info

## User Endpoints
- [x] GET `/api/v1/users/me` - Get current user profile
- [x] PUT `/api/v1/users/me` - Update current user settings
- [x] GET `/api/v1/users` - List all users
- [x] GET `/api/v1/users/{username}` - Get user by username

## Channel Endpoints
- [ ] POST `/api/v1/channels` - Create new channel
- [ ] GET `/api/v1/channels` - List all public channels
- [ ] GET `/api/v1/channels/me` - List user's channels
- [ ] GET `/api/v1/channels/{channel_id}` - Get channel details
- [ ] POST `/api/v1/channels/{channel_id}/join` - Join channel
- [ ] POST `/api/v1/channels/{channel_id}/leave` - Leave channel
- [ ] POST `/api/v1/channels/{channel_id}/members/{user_id}` - Add member to channel 