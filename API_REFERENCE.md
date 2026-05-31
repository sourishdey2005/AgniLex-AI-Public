# 📚 API Reference Documentation

Complete API reference for the AI Customer Support Agent Platform.

---

## Base URL

```
Local Development:  http://localhost:8000/api
Production:         https://your-domain.com/api
```

## Authentication

All protected endpoints require JWT token in Authorization header:

```
Authorization: Bearer <access_token>
```

Token obtained from login endpoint and expires after 30 minutes.

---

## 🔐 Authentication Endpoints

### POST /auth/signup

Create a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | Yes | 3-50 characters, alphanumeric |
| email | string | Yes | Valid email address |
| password | string | Yes | Minimum 8 characters |

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

**Error Responses:**
- `400 Bad Request` - Username or email already exists
- `422 Unprocessable Entity` - Invalid input format

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'
```

---

### POST /auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | Yes | Registered username |
| password | string | Yes | Account password |

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@localhost.local",
    "role": "admin"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - User account inactive

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

---

### POST /auth/change-password

Change user password (requires authentication).

**Request:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456",
  "confirm_password": "NewPassword456"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| current_password | string | Yes | Current password |
| new_password | string | Yes | New password (min 8 chars) |
| confirm_password | string | Yes | Confirmation of new password |

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Passwords don't match or invalid current password
- `401 Unauthorized` - Invalid token

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewPassword456",
    "confirm_password": "NewPassword456"
  }'
```

---

### GET /auth/me

Get current authenticated user info.

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@localhost.local",
  "role": "admin"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token

**Example:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

---

## 💬 Chat Endpoints

### POST /chat

Send a message and receive AI response.

**Request:**
```json
{
  "message": "What is your pricing?",
  "conversation_id": 5
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| message | string | Yes | User message (max 5000 chars) |
| conversation_id | integer | No | Existing conversation ID or null for new |

**Response (200 OK):**
```json
{
  "conversation_id": 5,
  "user_message": "What is your pricing?",
  "ai_response": "We offer flexible pricing plans...",
  "sentiment": "neutral",
  "category": "billing",
  "needs_escalation": false,
  "sources": [
    {
      "text": "Pricing: $29/month for basic plan..."
    }
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | ID of conversation (new or existing) |
| user_message | string | Echo of user message |
| ai_response | string | AI-generated response |
| sentiment | string | positive/negative/neutral |
| category | string | Query category (support/billing/feature_inquiry/refund_request/general) |
| needs_escalation | boolean | Whether human intervention needed |
| sources | array | Documents used for RAG context |

**Error Responses:**
- `400 Bad Request` - Invalid message format
- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - OpenAI API error

**Example:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "What is your pricing?",
    "conversation_id": null
  }'
```

---

### GET /conversations

List all conversations for authenticated user.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | integer | 50 | Max results to return |
| offset | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "New Chat",
    "created_at": "2024-01-15T10:30:00",
    "message_count": 5
  },
  {
    "id": 2,
    "title": "Pricing Question",
    "created_at": "2024-01-14T15:20:00",
    "message_count": 3
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token

**Example:**
```bash
curl -X GET "http://localhost:8000/api/conversations?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

---

### GET /conversations/{conversation_id}

Get specific conversation with all messages.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| conversation_id | integer | Conversation ID |

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "New Chat",
  "messages": [
    {
      "id": 1,
      "sender": "user",
      "content": "Hello, what is your pricing?",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "sender": "assistant",
      "content": "We offer flexible pricing...",
      "timestamp": "2024-01-15T10:30:05"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `404 Not Found` - Conversation not found or not owned by user

**Example:**
```bash
curl -X GET http://localhost:8000/api/conversations/1 \
  -H "Authorization: Bearer <token>"
```

---

### DELETE /conversations/{conversation_id}

Delete a conversation.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| conversation_id | integer | Conversation ID |

**Response (200 OK):**
```json
{
  "message": "Conversation deleted"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `404 Not Found` - Conversation not found

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/conversations/1 \
  -H "Authorization: Bearer <token>"
```

---

## 📄 Document Endpoints

### POST /upload

Upload and process a document.

**Request:**
- Content-Type: multipart/form-data
- File types: PDF, DOCX, TXT
- Max size: 50MB

**Form Data:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | file | Yes | Document file |

**Response (200 OK):**
```json
{
  "document_id": 5,
  "filename": "pricing.pdf",
  "chunks_created": 15,
  "status": "completed"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| document_id | integer | New document ID |
| filename | string | Uploaded filename |
| chunks_created | integer | Number of text chunks for search |
| status | string | Processing status |

**Error Responses:**
- `400 Bad Request` - Invalid file type
- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - Processing error

**Example:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@pricing.pdf"
```

---

### GET /documents

List all documents for authenticated user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "filename": "pricing.pdf",
    "file_type": "pdf",
    "status": "completed",
    "uploaded_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "filename": "faq.txt",
    "file_type": "txt",
    "status": "completed",
    "uploaded_at": "2024-01-14T15:20:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token

**Example:**
```bash
curl -X GET http://localhost:8000/api/documents \
  -H "Authorization: Bearer <token>"
```

---

### DELETE /documents/{document_id}

Delete a document.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| document_id | integer | Document ID |

**Response (200 OK):**
```json
{
  "message": "Document deleted"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `404 Not Found` - Document not found

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/documents/1 \
  -H "Authorization: Bearer <token>"
```

---

## 📊 Analytics Endpoints

### GET /analytics

Get user analytics and statistics.

**Response (200 OK):**
```json
{
  "total_queries": 42,
  "average_latency": 2.5,
  "sentiment": "positive",
  "total_conversations": 8,
  "total_documents": 3,
  "active": true
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| total_queries | integer | Total messages sent |
| average_latency | float | Average response time in ms |
| sentiment | string | Overall sentiment |
| total_conversations | integer | Number of conversations |
| total_documents | integer | Uploaded documents |
| active | boolean | Account active status |

**Error Responses:**
- `401 Unauthorized` - Invalid token

**Example:**
```bash
curl -X GET http://localhost:8000/api/analytics \
  -H "Authorization: Bearer <token>"
```

---

## 👨‍💼 Admin Endpoints

All admin endpoints require `role: "admin"` in JWT token.

### GET /admin/users

List all users in system.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | integer | 100 | Max results |
| offset | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@localhost.local",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-15T11:00:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin

**Example:**
```bash
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer <admin_token>"
```

---

### DELETE /admin/users/{user_id}

Delete a user and all their data.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | integer | User ID to delete |

**Response (200 OK):**
```json
{
  "message": "User deleted"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin
- `404 Not Found` - User not found

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/admin/users/2 \
  -H "Authorization: Bearer <admin_token>"
```

---

### GET /admin/statistics

Get platform-wide statistics.

**Response (200 OK):**
```json
{
  "total_users": 15,
  "active_users": 12,
  "total_conversations": 48,
  "total_documents": 23,
  "total_messages": 342
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin

**Example:**
```bash
curl -X GET http://localhost:8000/api/admin/statistics \
  -H "Authorization: Bearer <admin_token>"
```

---

### GET /admin/conversations

List all conversations system-wide.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 2,
    "title": "New Chat",
    "message_count": 5,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin

**Example:**
```bash
curl -X GET http://localhost:8000/api/admin/conversations \
  -H "Authorization: Bearer <admin_token>"
```

---

### DELETE /admin/conversations/{conversation_id}

Delete any conversation.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| conversation_id | integer | Conversation ID |

**Response (200 OK):**
```json
{
  "message": "Conversation deleted"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin
- `404 Not Found` - Conversation not found

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/admin/conversations/1 \
  -H "Authorization: Bearer <admin_token>"
```

---

### GET /admin/workflows

List workflow execution logs.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | integer | 100 | Max results |
| offset | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 2,
    "workflow_type": "chat",
    "status": "success",
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Not admin

**Example:**
```bash
curl -X GET http://localhost:8000/api/admin/workflows \
  -H "Authorization: Bearer <admin_token>"
```

---

## 🏥 Health Check

### GET /health

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 🔄 Rate Limiting

Current rate limits (can be customized):
- Chat: 30 requests/minute per user
- Upload: 10 requests/minute per user
- API calls: 100 requests/minute per user

Rate limit headers:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1705329600
```

---

## 📋 Common Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET /api/documents |
| 201 | Created | POST /api/auth/signup |
| 400 | Bad Request | Invalid JSON |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Admin endpoint as user |
| 404 | Not Found | Non-existent conversation |
| 422 | Invalid Input | Wrong data type |
| 500 | Server Error | OpenAI API down |

---

## 🔍 Query Examples

### Login and get token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.access_token')

echo $TOKEN
```

### Send chat message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is your support email?",
    "conversation_id": null
  }' | jq
```

### Upload document

```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@support_guide.pdf"
```

### Get analytics

```bash
curl -X GET http://localhost:8000/api/analytics \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 📚 Webhook Support (Coming Soon)

```json
POST /api/webhooks/register
{
  "event": "conversation_created",
  "url": "https://your-app.com/webhook"
}
```

---

## 🧪 Testing with Postman

1. Create new Postman collection
2. Add base URL: `http://localhost:8000/api`
3. Get token from `/auth/login`
4. Use token in Authorization tab for other requests
5. Import the complete API as collection

---

For interactive API testing, visit:
```
http://localhost:8000/docs
```

Swagger UI with live testing capability!
