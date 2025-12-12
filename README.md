
# Provider Data Validation & Directory Management System

A complete, production-quality AI-powered provider data validation system built for EY Techathon 6.0.

## 🎯 Features

- **Multi-format Upload**: Support for CSV and PDF (with OCR) file uploads
- **Agentic AI Pipeline**: 4 specialized AI agents working in sequence
  - Data Validation Agent
  - Information Enrichment Agent
  - Quality Assurance Agent
  - Directory Management Agent
- **External Validation**: NPI registry lookup, Google Maps validation, website scraping
- **Confidence Scoring**: Field-level and overall confidence scores
- **Analytics Dashboard**: Real-time statistics, charts, and provider management
- **Email Generation**: Automated email templates for review requests
- **Export Functionality**: Download validated results as CSV

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await
- **Database**: SQLite with SQLAlchemy ORM
- **Background Tasks**: Async validation pipeline
- **Agents**: Modular agentic AI system
- **Services**: Mock external API integrations

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Styling**: TailwindCSS with glassmorphism effects
- **State Management**: Zustand + React Query
- **Charts**: Recharts for data visualization
- **Animations**: Framer Motion

## 📁 Project Structure

```
.
├── backend/
│   ├── agents/           # AI agents (Validation, Enrichment, QA, Directory)
│   ├── config/           # Configuration settings
│   ├── database/         # Database models and connection
│   ├── models/           # Pydantic schemas
│   ├── routes/           # API endpoints
│   ├── services/         # External service integrations
│   ├── tasks/            # Background tasks
│   ├── utils/            # Utility functions
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
│
├── frontend/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── package.json      # Node dependencies
│
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Tesseract OCR (for PDF processing)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install Tesseract OCR**:
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. **Create .env file** (optional):
```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

6. **Run the backend**:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Create .env.local** (optional):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. **Run the frontend**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Database Schema

### ValidationJob
- `id`: Primary key
- `job_id`: Unique job identifier
- `status`: Job status (pending, processing, completed, failed)
- `total_providers`: Total number of providers
- `processed_providers`: Number of processed providers
- `created_at`, `updated_at`: Timestamps

### Provider
- `id`: Primary key
- `job_id`: Foreign key to ValidationJob
- `original_data`: JSON of original data
- Provider fields: `name`, `npi`, `specialty`, `phone`, `email`, `address`, `city`, `state`, `zip_code`, `website`
- Validated fields: `validated_name`, `validated_phone`, `validated_address`, etc.
- Confidence scores: `confidence_name`, `confidence_phone`, `confidence_address`, etc.
- Flags: `needs_review`, `is_suspicious`, `is_validated`
- `issues`: JSON array of issues
- `validation_notes`: Text notes

### ValidationLog
- `id`: Primary key
- `job_id`: Job identifier
- `provider_id`: Provider identifier
- `agent_name`: Agent that performed the action
- `action`: Action description
- `result`: JSON result
- `timestamp`: Action timestamp

## 🔄 Validation Pipeline Flow

1. **Upload**: User uploads CSV or PDF file
2. **Parse**: System extracts provider data
3. **Enrichment Agent**: Fills missing data from external sources
4. **Validation Agent**: Validates data against NPI registry, Google Maps, websites
5. **QA Agent**: Flags issues and calculates confidence scores
6. **Directory Agent**: Determines validation status and priority
7. **Results**: Provider data updated with validation results

## 📝 API Endpoints

### Upload
- `POST /api/upload/csv` - Upload CSV file
- `POST /api/upload/pdf` - Upload PDF file

### Validation
- `POST /api/validation/start` - Start validation job
- `GET /api/validation/status/{job_id}` - Get job status
- `GET /api/validation/providers/{job_id}` - Get providers list
- `GET /api/validation/provider/{provider_id}` - Get single provider

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/download-results` - Download results CSV

### Email
- `POST /api/email/template` - Generate email template

## 🎨 Frontend Pages

1. **Home Page** (`/`): Landing page with navigation
2. **Upload Page** (`/upload`): Drag & drop file upload
3. **Dashboard** (`/dashboard`): Analytics, charts, and provider table

## 🧪 Sample Data

See `sample_data/` directory for example CSV files with provider data.

## 🐳 Docker Support

### Backend
```bash
cd backend
docker build -t provider-validation-backend .
docker run -p 8000:8000 provider-validation-backend
```

## 📈 Demo Script

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Upload sample CSV file from `sample_data/providers.csv`
4. View validation progress on dashboard
5. Review provider details and generate email templates
6. Download validated results

## 🔧 Configuration

Key configuration options in `backend/config/settings.py`:
- `CONFIDENCE_THRESHOLD`: Minimum confidence for auto-validation (default: 0.7)
- `FUZZY_MATCH_THRESHOLD`: String matching threshold (default: 0.85)
- `MAX_UPLOAD_SIZE`: Maximum file size (default: 50MB)

## 📚 Technologies Used

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Tesseract OCR
- Pandas
- TheFuzz (fuzzy matching)

### Frontend
- Next.js 14
- TypeScript
- TailwindCSS
- React Query
- Zustand
- Recharts
- Framer Motion

## 🏆 Techathon Features

✅ Complete end-to-end prototype
✅ Agentic AI pipeline with 4 specialized agents
✅ Real-time validation with progress tracking
✅ Premium UI with glassmorphism design
✅ Comprehensive analytics dashboard
✅ Email template generation
✅ CSV export functionality
✅ Production-ready code architecture

## 📄 License

This project is built for EY Techathon 6.0.


=======
# provider-validation-system
AI-powered Provider Validation System using FastAPI &amp; Next.js. Upload CSV/PDF to extract, validate, and enrich provider data with OCR, fuzzy matching, and NPI API checks. Includes dashboards, logs, confidence scoring, and suspicious provider detection."
>>>>>>> c7e0161be22fd53a0a6d5b741187089071234cd9
