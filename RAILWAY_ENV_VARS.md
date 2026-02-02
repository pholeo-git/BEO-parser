# Railway Environment Variables Guide

Complete list of all environment variables needed for Railway deployment, with where to get each value.

## Step-by-Step Setup

### 1. Generate API Secret Key (Do this first)

**Variable Name:** `API_SECRET_KEY`

**How to get it:**
- Generate a secure random string
- You can use this command in your terminal:
  ```bash
  openssl rand -hex 32
  ```
- Or use an online generator: https://randomkeygen.com/
- Copy the generated string
- **This will be used for both Railway (backend) and Vercel (frontend)**

**Value Example:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

---

### 2. Set Up Supabase (Get 3 variables)

**First, create a Supabase project:**
1. Go to https://supabase.com
2. Sign up/Login
3. Click "New Project"
4. Fill in project details (name, database password, region)
5. Wait for project to be created (~2 minutes)

**Then get your Supabase credentials:**

#### Variable 1: `SUPABASE_URL`

**How to get it:**
1. In Supabase dashboard, go to **Settings** → **API**
2. Look for "Project URL"
3. Copy the URL (looks like: `https://xxxxxxxxxxxxx.supabase.co`)

**Value Example:** `https://abcdefghijklmnop.supabase.co`

---

#### Variable 2: `SUPABASE_KEY`

**How to get it:**
1. In Supabase dashboard, go to **Settings** → **API**
2. Look for "Project API keys"
3. Find the **"anon"** or **"public"** key
4. Click the eye icon to reveal it
5. Copy the key

**Value Example:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjIzOTAyMiwiZXhwIjoxOTMxODE1MDIyfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

#### Variable 3: `SUPABASE_SERVICE_KEY`

**How to get it:**
1. In Supabase dashboard, go to **Settings** → **API**
2. Look for "Project API keys"
3. Find the **"service_role"** key (⚠️ This is different from the anon key!)
4. Click the eye icon to reveal it
5. Copy the key
6. **⚠️ Keep this secret - it has admin privileges!**

**Value Example:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE5MzE4MTUwMjJ9.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

**After getting Supabase credentials, you also need to:**
- Run the database migration (see `backend/migrations/001_create_submissions_table.sql`)
- Create the storage bucket named `beo-outputs` (set to Private)
- Run the storage policies (see `backend/migrations/002_storage_policies.sql`)

---

### 3. Set Up Postmark (Get 2 variables)

**First, create a Postmark account:**
1. Go to https://postmarkapp.com
2. Sign up for an account
3. Verify your email

**Then verify your sending domain:**
1. In Postmark dashboard, go to **Sending** → **Domains**
2. Click "Add Domain"
3. Enter your domain (or use a subdomain)
4. Follow DNS setup instructions to verify
5. Wait for verification (can take a few minutes)

**Or use Postmark's test server (for testing):**
- You can use their test server without domain verification for initial testing

**Get your Postmark credentials:**

#### Variable 1: `POSTMARK_API_KEY`

**How to get it:**
1. In Postmark dashboard, go to **API Tokens**
2. Click "Create Token"
3. Give it a name (e.g., "BEO Separator")
4. Select "Server API Token" (not Account API Token)
5. Copy the token (you'll only see it once!)

**Value Example:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

#### Variable 2: `POSTMARK_FROM_EMAIL`

**How to get it:**
- This is the email address you verified in Postmark
- It should be from your verified domain
- Format: `noreply@yourdomain.com` or `hello@yourdomain.com`

**Value Example:** `noreply@pholeo.io` or `noreply@yourdomain.com`

**If using Postmark's test server:**
- Use: `test@blackhole.postmarkapp.com` (for testing only)

---

### 4. Set Configuration Variables (You set these directly)

These don't require external services - just set the values:

#### Variable 1: `CORS_ORIGINS`

**Value:** `http://localhost:3000`

**Note:** After you deploy to Vercel, update this to include your Vercel URL:
`http://localhost:3000,https://your-app.vercel.app`

---

#### Variable 2: `STORAGE_BUCKET_NAME`

**Value:** `beo-outputs`

---

#### Variable 3: `DOWNLOAD_URL_EXPIRY_DAYS`

**Value:** `30`

---

#### Variable 4: `RATE_LIMIT_PER_HOUR`

**Value:** `5`

---

## Complete Checklist for Railway

Add these 10 environment variables in Railway:

- [ ] `API_SECRET_KEY` - Generate with `openssl rand -hex 32`
- [ ] `CORS_ORIGINS` - Set to `http://localhost:3000`
- [ ] `SUPABASE_URL` - From Supabase Settings → API → Project URL
- [ ] `SUPABASE_KEY` - From Supabase Settings → API → anon/public key
- [ ] `SUPABASE_SERVICE_KEY` - From Supabase Settings → API → service_role key
- [ ] `POSTMARK_API_KEY` - From Postmark API Tokens → Server API Token
- [ ] `POSTMARK_FROM_EMAIL` - Your verified email address
- [ ] `STORAGE_BUCKET_NAME` - Set to `beo-outputs`
- [ ] `DOWNLOAD_URL_EXPIRY_DAYS` - Set to `30`
- [ ] `RATE_LIMIT_PER_HOUR` - Set to `5`

---

## Quick Reference: Where to Find Each Service

- **Supabase:** https://supabase.com/dashboard → Your Project → Settings → API
- **Postmark:** https://account.postmarkapp.com → API Tokens / Sending → Domains
- **Generate API Key:** Use `openssl rand -hex 32` in terminal

---

## After Adding All Variables

1. Railway will automatically redeploy
2. Check the deployment logs to ensure it starts successfully
3. Note your Railway backend URL (e.g., `https://your-service.railway.app`)
4. You'll need this URL for the frontend deployment
