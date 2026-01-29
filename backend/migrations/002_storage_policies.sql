-- Storage Policies for beo-outputs bucket
-- Run this in Supabase SQL Editor after creating the bucket

-- Allow service role to upload
CREATE POLICY "Service role can upload"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'beo-outputs' AND
        auth.role() = 'service_role'
    );

-- Allow service role to read
CREATE POLICY "Service role can read"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'beo-outputs' AND
        auth.role() = 'service_role'
    );

-- Allow service role to delete
CREATE POLICY "Service role can delete"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'beo-outputs' AND
        auth.role() = 'service_role'
    );
