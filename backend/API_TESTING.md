# API Testing Guide

This guide shows you how to test the NexusHR AI Backend API using curl commands or the Swagger UI.

## Prerequisites

- Backend server running on `http://localhost:8000`
- Terminal or command prompt
- curl installed (for command-line testing)

## 1. Health Check

Check if the server is running:

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "rag_system_initialized": true,
  "timestamp": "2025-12-17T..."
}
```

## 2. Authentication

### Login as HR Manager

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the access_token for subsequent requests!**

### Get Current User Info

```bash
# Replace YOUR_TOKEN with the actual token
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 3. Document Management

### Upload a Document

First, create a sample PDF or use an existing one:

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/Employee_Handbook.pdf"
```

Response:
```json
{
  "status": "success",
  "message": "Successfully ingested document: Employee_Handbook.pdf",
  "chunks_created": 45,
  "pages_processed": 15,
  "document_id": "20251217_120000_Employee_Handbook.pdf"
}
```

### Get Collection Statistics

```bash
curl -X GET "http://localhost:8000/api/documents/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Uploaded Documents

```bash
curl -X GET "http://localhost:8000/api/documents/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 4. Querying the System

### Simple Query

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many sick leaves do employees get?",
    "include_sources": true
  }'
```

Response:
```json
{
  "status": "success",
  "answer": "According to the company policy, each employee is entitled to 12 days of sick leave per year...",
  "sources": [
    {
      "content": "LEAVE POLICY - SECTION 4.2...",
      "metadata": {
        "filename": "Employee_Handbook.pdf",
        "page": 5
      }
    }
  ],
  "question": "How many sick leaves do employees get?",
  "intent": "policy",
  "suggestions": [
    "Can sick leave be encashed?",
    "How do I apply for sick leave?",
    "What is the privilege leave policy?"
  ]
}
```

### Query with Chat History

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can it be encashed?",
    "chat_history": [
      {
        "question": "How many sick leaves do employees get?",
        "answer": "Each employee gets 12 sick leaves per year."
      }
    ],
    "include_sources": true
  }'
```

### Classify Intent

```bash
curl -X POST "http://localhost:8000/api/chat/classify-intent?question=How%20many%20sick%20leaves?" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 5. Testing Complete Workflow

### Step 1: Login

```bash
# Save token to variable
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Step 2: Check System Status

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/chat/health
```

### Step 3: Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Employee_Handbook.pdf"
```

### Step 4: Query the System

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the leave policy?",
    "include_sources": true
  }' | jq
```

## 6. Using Swagger UI (Easier Method)

1. Start the backend server:
   ```bash
   python run.py
   ```

2. Open browser and go to: `http://localhost:8000/api/docs`

3. Click on **"Authorize"** button (top right)

4. Login:
   - Click on `POST /api/auth/login`
   - Click "Try it out"
   - Enter credentials:
     - username: `hr_manager`
     - password: `manager123`
   - Click "Execute"
   - Copy the `access_token` from the response

5. Authorize:
   - Click the **"Authorize"** button again
   - Paste the token in the value field
   - Click "Authorize"
   - Click "Close"

6. Now you can test any endpoint:
   - Upload document: `POST /api/documents/upload`
   - Query system: `POST /api/chat/query`
   - Get stats: `GET /api/documents/stats`

## 7. Sample Questions to Test

Try these questions after uploading an HR policy document:

### Leave Policies
- "How many sick leaves do employees get?"
- "Can sick leave be encashed?"
- "What is the privilege leave policy?"
- "How many days of maternity leave?"

### Working Hours
- "What are the working hours?"
- "Is remote work allowed?"
- "What is the overtime policy?"

### Salary & Compensation
- "When is the salary paid?"
- "What are the salary components?"
- "How is the bonus calculated?"

### Performance
- "How is performance evaluated?"
- "When is the appraisal cycle?"
- "What are the promotion criteria?"

## 8. Common Issues

### "Could not validate credentials"
- Token might be expired (30 min default)
- Login again to get a new token

### "No documents found" or empty response
- Upload a document first using `POST /api/documents/upload`
- Check if document was ingested successfully

### Connection refused
- Make sure the server is running: `python run.py`
- Check if port 8000 is available

## 9. Admin-Only Operations

Login as admin:
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_admin&password=admin123" | jq -r '.access_token')
```

Delete all documents (careful!):
```bash
curl -X DELETE "http://localhost:8000/api/documents/all" \
  -H "Authorization: Bearer $TOKEN"
```

## 10. Performance Testing

Test multiple queries in sequence:
```bash
for question in \
  "How many sick leaves?" \
  "What are working hours?" \
  "When is salary paid?" \
  "How is performance reviewed?"; do
  
  echo "Question: $question"
  curl -s -X POST "http://localhost:8000/api/chat/query" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"$question\"}" | jq -r '.answer'
  echo "---"
done
```

---

Happy Testing! 🚀
