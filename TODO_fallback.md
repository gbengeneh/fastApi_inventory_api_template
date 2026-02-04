# TODO: Implement Fallback to Supabase Python Client

## Steps to Complete

- [x] Update requirements.txt to add supabase package
- [x] Modify database.py to initialize Supabase client and update is_online() for fallback check
- [x] Refactor sync.py to use PostgreSQL SQLAlchemy if available, else Supabase client for API-based sync
- [x] Test the fallback mechanism (run sync and verify both paths work)

## Notes
- PostgreSQL connection string: postgresql://postgres:Gbenga12%40%2312@db.bvmgydhrvufwubjecmzm.supabase.co:5432/postgres
- SUPABASE_URL: https://bvmgydhrvufwubjecmzm.supabase.co
- SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2bWd5ZGhydnVmd3ViamVjbXptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2NzY3ODYsImV4cCI6MjA3NzI1Mjc4Nn0.o6OxswT6flVsGjM4dr2S-NliqFRW8mOAEx0vDJbhPx0
- For Supabase sync, serialize SQLAlchemy records to dicts and use supabase.table().upsert()
- Ensure table names match model names (e.g., Organization -> organizations)
- Fixed datetime serialization for Supabase
- Reordered sync to respect foreign key constraints (organizations, outlets, users, etc.)
