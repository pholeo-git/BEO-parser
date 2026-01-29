-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    event_name TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    download_url TEXT,
    error_message TEXT,
    file_size BIGINT,
    beo_count INTEGER
);

-- Create index on email for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_submissions_email ON submissions(email);

-- Create index on created_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at);

-- Create index on status for status queries
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

-- Enable Row Level Security (optional, can be configured later)
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow service role to do everything (for backend API)
CREATE POLICY "Service role can manage submissions"
    ON submissions
    FOR ALL
    USING (auth.role() = 'service_role');
