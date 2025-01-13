# API Reference

## Server Information

## Endpoints

### POST /api/v1/auth/register

Register

Register a new user.

**Request Body:**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UserCreate"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/auth/login

Login

Login user.

**Request Body:**

```json
{
  "content": {
    "application/x-www-form-urlencoded": {
      "schema": {
        "$ref": "#/components/schemas/Body_login_api_v1_auth_login_post"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/auth/me

Get Current User

Get current user.

**Responses:**

- 200: Successful Response

---

### GET /api/v1/channels

Get Channels

Get all public channels.

**Responses:**

- 200: Successful Response

---

### POST /api/v1/channels

Create Channel

Create a new channel.

**Request Body:**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ChannelCreate"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 201: Successful Response
- 422: Validation Error

---

### GET /api/v1/channels/me

Get My Channels

Get channels where the current user is a member.

**Responses:**

- 200: Successful Response

---

### GET /api/v1/channels/{channel_id}

Get Channel

Get a specific channel by ID.

**Parameters:**

- `channel_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/channels/{channel_id}/join

Join Channel

Join a channel.

**Parameters:**

- `channel_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/channels/{channel_id}/leave

Leave Channel

Leave a channel.

**Parameters:**

- `channel_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/channels/{channel_id}/members/{user_id}

Add Member

Add a member to a channel.

**Parameters:**

- `channel_id` (path): 
- `user_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/channels/{channel_id}/messages/{message_id}/reactions

Add Reaction

Add a reaction to a message in a channel.

**Parameters:**

- `channel_id` (path): 
- `message_id` (path): 
- `emoji` (query): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/channels/{channel_id}/messages/{message_id}/reactions

Get Message Reactions

Get all reactions for a message in a channel.

**Parameters:**

- `channel_id` (path): 
- `message_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### DELETE /api/v1/channels/{channel_id}/messages/{message_id}/reactions/{emoji}

Remove Reaction

Remove a reaction from a message in a channel.

**Parameters:**

- `channel_id` (path): 
- `message_id` (path): 
- `emoji` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/messages

Create Message

Create a new message.

**Request Body:**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/MessageCreate"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/messages/{message_id}

Get Message

Get a specific message.

**Parameters:**

- `message_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### DELETE /api/v1/messages/{message_id}

Delete Message

Delete a message.

**Parameters:**

- `message_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/users/me

Get Current User Profile

Get current user's profile.

**Responses:**

- 200: Successful Response

---

### PUT /api/v1/users/me

Update User Settings

Update current user's settings.

**Request Body:**

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UserUpdate"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/users

Get Users

Get all users.

**Responses:**

- 200: Successful Response

---

### GET /api/v1/users/{username}

Get User By Username

Get a specific user by username.

**Parameters:**

- `username` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### POST /api/v1/files/upload

Upload File

Upload a file.

**Request Body:**

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "$ref": "#/components/schemas/Body_upload_file_api_v1_files_upload_post"
      }
    }
  },
  "required": true
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/files/{file_id}/metadata

Get File Metadata

Get file metadata.

**Parameters:**

- `file_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /api/v1/files/{file_id}

Get File

Download a file.

**Parameters:**

- `file_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### DELETE /api/v1/files/{file_id}

Delete File

Delete a file.

**Parameters:**

- `file_id` (path): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

### GET /

Root

Health check endpoint.

**Responses:**

- 200: Successful Response

---

