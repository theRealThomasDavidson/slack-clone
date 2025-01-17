# API Testing with cURL

This document provides a collection of cURL commands for testing the Chat API endpoints.

## Authentication Endpoints

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

Expected Response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-23T12:00:00",
  "updated_at": "2024-01-23T12:00:00"
}
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Expected Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

### 3. Get Current User Profile
```bash
# Replace {token} with the actual token received from login
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {token}"
```

Expected Response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-23T12:00:00",
  "updated_at": "2024-01-23T12:00:00"
}
```

## Channel Endpoints

### 1. Create Channel
```bash
curl -X POST "http://localhost:8000/api/v1/channels" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "general",
    "description": "General discussion channel"
  }'
```

Expected Response:
```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion channel",
  "is_private": false,
  "created_at": "2024-01-23T12:00:00",
  "updated_at": "2024-01-23T12:00:00"
}
```

### 2. List Channels
```bash
curl -X GET "http://localhost:8000/api/v1/channels" \
  -H "Authorization: Bearer {token}"
```

Expected Response:
```json
[
  {
    "id": 1,
    "name": "general",
    "description": "General discussion channel",
    "is_private": false,
    "created_at": "2024-01-23T12:00:00",
    "updated_at": "2024-01-23T12:00:00"
  }
]
```

## Message Endpoints

### 1. Send Message
```bash
curl -X POST "http://localhost:8000/api/v1/chat/messages" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, world!",
    "channel_id": 1
  }'
```

Expected Response:
```json
{
  "id": 1,
  "content": "Hello, world!",
  "user_id": 1,
  "channel_id": 1,
  "created_at": "2024-01-23T12:00:00",
  "updated_at": "2024-01-23T12:00:00"
}
```

### 2. Get Channel Messages
```bash
curl -X GET "http://localhost:8000/api/v1/chat/messages/1" \
  -H "Authorization: Bearer {token}"
```

Expected Response:
```json
[
  {
    "id": 1,
    "content": "Hello, world!",
    "user_id": 1,
    "channel_id": 1,
    "created_at": "2024-01-23T12:00:00",
    "updated_at": "2024-01-23T12:00:00"
  }
]
```

## Testing Script

Here's a bash script that runs through the basic test flow:

```bash
#!/bin/bash

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Register user
echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }')
echo $REGISTER_RESPONSE

# Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# Create channel
echo "Creating channel..."
CHANNEL_RESPONSE=$(curl -s -X POST "$BASE_URL/channels" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "general",
    "description": "General discussion channel"
  }')
CHANNEL_ID=$(echo $CHANNEL_RESPONSE | jq -r '.id')
echo $CHANNEL_RESPONSE

# Send message
echo "Sending message..."
MESSAGE_RESPONSE=$(curl -s -X POST "$BASE_URL/chat/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Hello, world!\",
    \"channel_id\": $CHANNEL_ID
  }")
echo $MESSAGE_RESPONSE
```

## PowerShell Testing Script

For Windows users, here's a PowerShell version of the test script:

```powershell
# Base URL
$BASE_URL = "http://localhost:8000/api/v1"

# Register user
Write-Host "Registering user..."
$registerBody = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/auth/register" `
    -ContentType "application/json" -Body $registerBody
$registerResponse | ConvertTo-Json

# Login
Write-Host "Logging in..."
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/auth/token" `
    -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access_token
Write-Host "Token: $token"

# Create channel
Write-Host "Creating channel..."
$channelBody = @{
    name = "general"
    description = "General discussion channel"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
}

$channelResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/channels" `
    -ContentType "application/json" -Headers $headers -Body $channelBody
$channelId = $channelResponse.id
$channelResponse | ConvertTo-Json

# Send message
Write-Host "Sending message..."
$messageBody = @{
    content = "Hello, world!"
    channel_id = $channelId
} | ConvertTo-Json

$messageResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/chat/messages" `
    -ContentType "application/json" -Headers $headers -Body $messageBody
$messageResponse | ConvertTo-Json
```

## Notes

1. Replace `{token}` in the examples with an actual JWT token obtained from the login endpoint.
2. The PowerShell script uses `Invoke-RestMethod` which handles the HTTP requests more naturally in Windows environments.
3. The bash script requires `jq` for JSON parsing.
4. All timestamps in responses are in UTC.
``` 