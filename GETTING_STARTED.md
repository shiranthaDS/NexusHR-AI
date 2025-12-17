# 🎬 Quick Start Guide - NexusHR AI

This guide will get you up and running with NexusHR AI in under 5 minutes!

## ⚡ Super Quick Start (macOS/Linux)

```bash
# 1. Navigate to backend
cd backend

# 2. Run setup script (does everything for you!)
./setup.sh

# 3. Start the server
source venv/bin/activate
python run.py
```

That's it! 🎉 Your server is running at http://localhost:8000

## 📱 Using the API

### Step 1: Open API Documentation

Open your browser and go to:
```
http://localhost:8000/api/docs
```

### Step 2: Login

1. Find `POST /api/auth/login` endpoint
2. Click "Try it out"
3. Enter credentials:
   - Username: `hr_manager`
   - Password: `manager123`
4. Click "Execute"
5. Copy the `access_token` from the response

### Step 3: Authorize

1. Click the **"Authorize"** button (🔒 icon, top right)
2. Paste your token in the "Value" field
3. Click "Authorize"
4. Click "Close"

### Step 4: Upload a Document

1. Find `POST /api/documents/upload` endpoint
2. Click "Try it out"
3. Click "Choose File" and select a PDF
4. Click "Execute"

**Don't have a PDF?** No problem! We'll create a sample one:

```bash
# In backend directory
python sample_data.py
```

This creates `Employee_Handbook_Sample.txt` - you'll need to convert it to PDF or use your own HR policy PDF.

### Step 5: Ask Questions!

1. Find `POST /api/chat/query` endpoint
2. Click "Try it out"
3. Enter this JSON:
```json
{
  "question": "How many sick leaves do employees get?",
  "include_sources": true
}
```
4. Click "Execute"
5. See the AI-generated answer with sources! 🎉

## 🎯 Sample Questions to Try

After uploading an HR policy document, try these:

### Leave Policies
```
"How many sick leaves do employees get?"
"Can sick leave be encashed?"
"What is the privilege leave policy?"
"How many days of maternity leave?"
```

### Working Hours
```
"What are the working hours?"
"Is remote work allowed?"
"What is the overtime policy?"
```

### Salary
```
"When is the salary paid?"
"What are the salary components?"
"How is the bonus calculated?"
```

### Performance
```
"How is performance evaluated?"
"When is the appraisal cycle?"
"What are the promotion criteria?"
```

## 🔧 Manual Setup (If ./setup.sh doesn't work)

### Step 1: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes as it downloads several packages.

### Step 3: Create Directories

```bash
mkdir -p uploads chroma_db
```

### Step 4: Verify Setup

```bash
python test_setup.py
```

You should see:
```
✅ PASS - Package Installation
✅ PASS - Environment Configuration
✅ PASS - Directory Structure
✅ PASS - RAG System
```

### Step 5: Start Server

```bash
python run.py
```

## 🌐 Using curl (Command Line)

### 1. Login and Save Token

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123" | jq -r '.access_token')

echo "Your token: $TOKEN"
```

### 2. Check Health

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/health | jq
```

### 3. Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/document.pdf" | jq
```

### 4. Ask Question

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many sick leaves do employees get?",
    "include_sources": true
  }' | jq
```

## 🎨 User Roles & Access

| Role | Username | Password | Can Upload Docs | Can Query | Can Delete All |
|------|----------|----------|----------------|-----------|----------------|
| Admin | hr_admin | admin123 | ✅ | ✅ | ✅ |
| HR Manager | hr_manager | manager123 | ✅ | ✅ | ❌ |
| Employee | employee | employee123 | ❌ | ✅ | ❌ |

## 🔍 Checking if Everything Works

### Test 1: Server is Running
```bash
curl http://localhost:8000/
```
Should return: `{"message": "Welcome to NexusHR AI Backend", ...}`

### Test 2: RAG System Initialized
```bash
curl http://localhost:8000/api/health
```
Should return: `{"status": "healthy", "rag_system_initialized": true, ...}`

### Test 3: Authentication Works
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=employee&password=employee123"
```
Should return an access token.

## 🐛 Common Issues & Solutions

### Issue: "Port 8000 already in use"

**Solution 1**: Kill the process
```bash
lsof -i :8000
kill -9 <PID>
```

**Solution 2**: Change port in `.env`
```bash
echo "API_PORT=8001" >> .env
python run.py
```

### Issue: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated
```bash
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Issue: "ChromaDB initialization error"

**Solution**: Clear and restart
```bash
rm -rf chroma_db/
python run.py
```

### Issue: Models taking long to load

**Solution**: This is normal on first run! Models are being downloaded from Hugging Face.
- all-MiniLM-L6-v2: ~90MB
- Mistral-7B: ~14GB (only model metadata, actual inference via API)

Wait a few minutes and you'll see:
```
✅ RAG System initialized successfully
```

### Issue: "Could not validate credentials"

**Solution**: Token expired (30 min default). Login again:
```bash
# Get new token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123" | jq -r '.access_token')
```

## 📝 Next Steps

1. ✅ Got the server running
2. ✅ Can login and get token
3. ✅ Can upload documents
4. ✅ Can query the system

**Now you can:**
- 🎓 Present this to your examiners/interviewers
- 💻 Build the frontend with Next.js
- 🚀 Deploy to cloud (AWS/Azure/GCP)
- 📊 Add more features (analytics, history, etc.)

## 💡 Tips for Demo/Presentation

1. **Start server BEFORE your presentation**
   - Models take time to load first time
   - Test all endpoints beforehand

2. **Prepare sample documents**
   - Have 2-3 HR policy PDFs ready
   - Know what questions to ask

3. **Use Swagger UI for live demo**
   - More visual than curl
   - Shows all endpoints clearly

4. **Explain the flow**
   - Show document upload
   - Ask a question
   - Point out source citations
   - Show follow-up suggestions

5. **Highlight technical aspects**
   - RAG architecture
   - Vector similarity search
   - LLM integration
   - Role-based access

## 🎉 You're All Set!

Your NexusHR AI backend is ready to impress! 

**Questions?** Check:
- [README.md](../README.md) - Full documentation
- [API_TESTING.md](API_TESTING.md) - Detailed API testing
- [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) - Architecture details

**Happy coding!** 🚀
