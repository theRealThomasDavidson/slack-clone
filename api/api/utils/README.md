# Utilities Documentation

## Overview
Utility modules providing reusable functionality across the Chat API. Each module follows SOLID principles and provides focused, single-purpose tools.

## WebSocket Manager (`websocket.py`)

**Description**: Manages real-time WebSocket connections and message broadcasting  
**Input**:
- WebSocket connections
- User IDs
- Channel IDs
- Message payloads  
**Output**:
- Connection states
- Broadcast confirmations
- Connection events

### Key Features
- Connection lifecycle management
- User session tracking
- Channel subscription handling
- Message broadcasting
- Connection state management

## Validation (`validation.py`)

**Description**: Input validation and sanitization utilities  
**Input**:
- Usernames
- Emails
- Passwords
- Message content
- File metadata  
**Output**:
- Validation results
- Sanitized content
- Error messages

### Key Features
- Username format validation
- Email format validation
- Password strength checking
- Content sanitization
- Input normalization

## File Handling (`files.py`)

**Description**: File storage and retrieval operations  
**Input**:
- File data
- File metadata
- Storage paths
- User context  
**Output**:
- File identifiers
- Storage locations
- Access URLs
- Error states

### Key Features
- File upload processing
- Storage management
- File type validation
- Path management
- URL generation

## Time Utilities (`time.py`)

**Description**: Time-related formatting and calculations  
**Input**:
- Timestamps
- Time zones
- Duration values
- Format specifications  
**Output**:
- Formatted timestamps
- Time differences
- Duration strings
- Timezone-aware dates

### Key Features
- Timestamp formatting
- Duration calculations
- Timezone handling
- Human-readable formats
- Date comparisons

## Rate Limiting (`rate_limit.py`)

**Description**: Request rate limiting implementation  
**Input**:
- Request identifiers
- Time windows
- Rate limits
- User context  
**Output**:
- Allow/deny decisions
- Remaining quota
- Reset times
- Error states

### Key Features
- Request counting
- Window management
- Limit enforcement
- Key management
- Cleanup operations

## Error Handling

**Description**: Standardized error handling utilities  
**Input**:
- Error types
- Error contexts
- Stack traces  
**Output**:
- Error responses
- Log entries
- Client messages

### Key Features
- Specific error types
- Meaningful messages
- Error categorization
- Proper propagation
- Recovery strategies

## Performance Utilities

**Description**: Performance optimization tools  
**Input**:
- Resource usage data
- Performance thresholds
- Operation contexts  
**Output**:
- Performance metrics
- Optimization suggestions
- Resource states

### Key Features
- Caching strategies
- Lazy loading
- Resource pooling
- Batch operations
- Cleanup routines

## Running Tests

```bash
pytest api/tests/test_utils/
```

## Extension Points

### Custom Implementations
- Storage backends
- Validation rules
- Rate limiting strategies
- Time formatters
- Broadcasting strategies

### Event Hooks
- Pre/post validation
- File operations
- Rate limit checks
- Connection events
- Message processing 