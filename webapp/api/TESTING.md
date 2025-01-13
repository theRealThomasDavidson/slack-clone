# API Testing Guide

This document contains example commands for testing the API endpoints.

## Authentication

### Register a New User
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = '{"username": "testuser2", "email": "test2@example.com", "password": "testpass123"}'
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/auth/register" -Headers $headers -Body $body

# Expected Response:
{
    "email": "test2@example.com",
    "username": "testuser2",
    "id": 2,
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-01-09T18:36:36.735044",
    "updated_at": "2025-01-09T18:36:36.735050"
}
```

### Login (Get Token)
```powershell
$headers = @{ "Content-Type" = "application/x-www-form-urlencoded" }
$body = "username=testuser2&password=testpass123"
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/auth/token" -Headers $headers -Body $body

# Expected Response:
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### Get Current User
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Get -Uri "http://localhost:8000/api/v1/auth/me" -Headers $headers

# Expected Response:
{
    "email": "test2@example.com",
    "username": "testuser2",
    "id": 2,
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-01-09T18:36:36.735044",
    "updated_at": "2025-01-09T18:36:36.735050"
}
```

## Channels

### Create Public Channel
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ 
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json" 
}
$body = '{
    "name": "Random",
    "description": "Random discussions",
    "is_private": false
}'
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/channels/" -Headers $headers -Body $body

# Expected Response:
{
    "name": "Random",
    "description": "Random discussions",
    "is_private": false,
    "id": 2,
    "created_at": "2025-01-09T18:37:09.717966",
    "updated_at": "2025-01-09T18:37:09.717973"
}
```

### Create Private Channel
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ 
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json" 
}
$body = '{
    "name": "Secret",
    "description": "Private discussions",
    "is_private": true
}'
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/channels/" -Headers $headers -Body $body
```

### List All Channels
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Get -Uri "http://localhost:8000/api/v1/channels/" -Headers $headers

# Expected Response:
[
    {
        "name": "General",
        "description": "General discussion channel",
        "is_private": false,
        "id": 1,
        "created_at": "2025-01-09T18:35:10.239763",
        "updated_at": "2025-01-09T18:35:10.239766"
    },
    {
        "name": "Random",
        "description": "Random discussions",
        "is_private": false,
        "id": 2,
        "created_at": "2025-01-09T18:37:09.717966",
        "updated_at": "2025-01-09T18:37:09.717973"
    }
]
```

### Get My Channels
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Get -Uri "http://localhost:8000/api/v1/channels/me" -Headers $headers
```

### Get Specific Channel
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Get -Uri "http://localhost:8000/api/v1/channels/1" -Headers $headers
```

### Join Channel
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/channels/1/join" -Headers $headers
```

### Leave Channel
```powershell
$token = "YOUR_ACCESS_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/channels/1/leave" -Headers $headers
```

## Error Responses

### Unauthorized (401)
```json
{
    "detail": "Not authenticated"
}
```

### Channel Not Found (404)
```json
{
    "detail": "Channel not found"
}
```

### Already Member (400)
```json
{
    "detail": "User is already a member of this channel"
}
```

### Not Member (400)
```json
{
    "detail": "User is not a member of this channel"
}
```

## Notes

1. Replace `YOUR_ACCESS_TOKEN` with the actual token received from the login endpoint.
2. All timestamps are in UTC.
3. These examples use PowerShell commands. For Unix-like systems, use equivalent curl commands.
4. The server should be running at `http://localhost:8000`.
5. Private channels are only visible to their members.
6. Channel IDs in the examples should be replaced with actual channel IDs from your system. 