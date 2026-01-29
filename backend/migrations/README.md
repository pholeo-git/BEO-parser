# Database Migrations

## Running Migrations

### Using Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the migration files in order

### Using Supabase CLI
```bash
supabase db push
```

## Migration Files

### 001_create_submissions_table.sql
Creates the `submissions` table with all required fields and indexes.

## Storage Bucket Setup

After running the database migration, create the storage bucket:

1. Go to Storage in Supabase Dashboard
2. Create a new bucket named `beo-outputs`
3. Set it to **Private** (we'll use signed URLs)
4. Configure policies:
   - Allow service role to upload files
   - Allow service role to create signed URLs
   - Allow service role to delete files

### Storage Policy SQL (run in SQL Editor):
```sql
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
```
