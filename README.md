# BEO Separator Web Application

Full-stack web application for splitting BEO packet PDFs into individual BEO files.

## Architecture

- **Frontend**: Next.js 14+ with TypeScript (deployed on Vercel)
- **Backend**: FastAPI (deployed on Railway/Render)
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage
- **Email**: Postmark

## Setup

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
API_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
POSTMARK_API_KEY=your-postmark-api-key
POSTMARK_FROM_EMAIL=noreply@yourdomain.com
STORAGE_BUCKET_NAME=beo-outputs
DOWNLOAD_URL_EXPIRY_DAYS=30
```

5. Run database migrations (see `backend/migrations/README.md`)

6. Start the server:
```bash
uvicorn app.main:app --reload
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-secret-key-here
```

4. Start development server:
```bash
npm run dev
```

## Deployment

### Backend (Railway/Render)

1. Connect your GitHub repository
2. Set environment variables in the platform dashboard
3. Deploy using the Dockerfile

### Frontend (Vercel)

1. Connect your GitHub repository
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
   - `NEXT_PUBLIC_API_KEY` - Your API secret key
3. Deploy

## Security Features

- API key authentication
- File type validation (PDF only)
- CORS configuration
- Input sanitization
- Signed URLs with expiration
- Rate limiting (configurable)

## License

MIT
