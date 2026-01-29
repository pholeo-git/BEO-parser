# Deployment Guide

## Prerequisites

1. GitHub account and repository
2. Supabase account and project
3. Postmark account
4. Vercel account (for frontend)
5. Railway or Render account (for backend)

## Step 1: Supabase Setup

1. Create a new Supabase project
2. Go to SQL Editor and run `backend/migrations/001_create_submissions_table.sql`
3. Go to Storage and create a bucket named `beo-outputs` (set to Private)
4. Run the storage policies SQL from `backend/migrations/README.md`
5. Get your project URL and API keys from Settings > API

## Step 2: Postmark Setup

1. Create a Postmark account
2. Verify your sending domain
3. Get your API key from API Tokens
4. Note your verified sender email address

## Step 3: Backend Deployment (Railway)

1. Go to Railway dashboard
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `backend`
5. Add environment variables:
   ```
   API_SECRET_KEY=<generate-a-secure-random-string>
   CORS_ORIGINS=https://your-frontend.vercel.app
   SUPABASE_URL=<from-supabase>
   SUPABASE_KEY=<from-supabase>
   SUPABASE_SERVICE_KEY=<from-supabase>
   POSTMARK_API_KEY=<from-postmark>
   POSTMARK_FROM_EMAIL=<your-verified-email>
   STORAGE_BUCKET_NAME=beo-outputs
   DOWNLOAD_URL_EXPIRY_DAYS=30
   RATE_LIMIT_PER_HOUR=5
   ```
6. Railway will automatically detect the Dockerfile and deploy

## Step 4: Backend Deployment (Render)

1. Go to Render dashboard
2. Click "New" > "Web Service"
3. Connect your GitHub repository
4. Set:
   - Name: `beo-separator-api`
   - Root Directory: `backend`
   - Environment: `Docker`
   - Build Command: (leave empty, uses Dockerfile)
   - Start Command: (leave empty, uses Dockerfile)
5. Add environment variables (same as Railway above)
6. Deploy

## Step 5: Frontend Deployment (Vercel)

1. Go to Vercel dashboard
2. Click "Add New" > "Project"
3. Import your GitHub repository
4. Set:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
5. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app (or .render.com)
   NEXT_PUBLIC_API_KEY=<same-as-backend-API_SECRET_KEY>
   ```
6. Deploy

## Step 6: Update CORS

After frontend is deployed, update backend `CORS_ORIGINS` to include your Vercel URL.

## Verification

1. Visit your Vercel frontend URL
2. Fill out the form and upload a test PDF
3. Check that you receive an email with download link
4. Verify the download works

## Monitoring

- Backend: Check Railway/Render logs for errors
- Frontend: Check Vercel logs
- Database: Monitor Supabase dashboard for submissions
- Storage: Check Supabase Storage usage
