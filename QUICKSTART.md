# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt
# Start server
uvicorn main:app --reload --port 8000
```

✅ Backend running at: http://localhost:8000
✅ API docs at: http://localhost:8000/docs

### Step 2: Frontend Setup (2 minutes)

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

### Step 3: Test the System (1 minute)

1. Open browser: http://localhost:3000
2. Click "Upload Data"
3. Upload `sample_data/providers.csv`
4. Navigate to Dashboard
5. Watch validation progress!

## 📋 Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Tesseract OCR installed (for PDF support)
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
**Solution**: Make sure virtual environment is activated and dependencies are installed

**Problem**: `Port 8000 already in use`
**Solution**: Change port: `uvicorn main:app --reload --port 8001`

**Problem**: Tesseract not found
**Solution**: Install Tesseract OCR (see Prerequisites)

### Frontend Issues

**Problem**: `npm install` fails
**Solution**: Make sure Node.js 18+ is installed

**Problem**: API connection errors
**Solution**: Check backend is running and `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL

## 🎯 Next Steps

1. Read `README.md` for full documentation
2. Review `ARCHITECTURE.md` for system design
3. Check `DEMO_SCRIPT.md` for presentation guide
4. Explore `sample_data/` for example files

## 💡 Tips

- Backend auto-reloads on code changes (--reload flag)
- Frontend hot-reloads automatically
- Check browser console for frontend errors
- Check terminal for backend errors
- API docs at `/docs` show all endpoints

