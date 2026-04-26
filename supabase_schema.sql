-- ========================================================
-- LAW ASSIST AI - SUPABASE SCHEMA (FULL MIGRATION)
-- ========================================================

-- 1. Enable Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Clients Table
CREATE TABLE IF NOT EXISTS public.client (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL,
    trello_card_id TEXT,
    drive_folder_id TEXT,
    contract_doc_id TEXT,
    contract_doc_url TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_client_phone ON public.client(phone);

-- 3. Leads Table
CREATE TABLE IF NOT EXISTS public.lead (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    legal_area TEXT,
    urgency TEXT DEFAULT 'medium',
    summary TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lead_phone ON public.lead(phone);

-- 4. Transactions Table (Finance)
CREATE TABLE IF NOT EXISTS public.transaction (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES public.client(id),
    lead_id INTEGER REFERENCES public.lead(id),
    type TEXT NOT NULL, -- 'income', 'expense'
    category TEXT NOT NULL, -- 'honorarios', 'custas', 'outros'
    amount DOUBLE PRECISION NOT NULL,
    description TEXT,
    date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Users Table (Auth Profile)
CREATE TABLE IF NOT EXISTS public.user (
    id UUID PRIMARY KEY, -- Matches Supabase Auth User ID
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'attorney',
    escritorio_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Knowledge Base Table (RAG)
CREATE TABLE IF NOT EXISTS public.knowledgechunk (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- Match OpenAI text-embedding-3-small
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Supabase Auth Trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.user (id, email, role, escritorio_id, full_name)
  VALUES (
    new.id, 
    new.email, 
    COALESCE(new.raw_user_meta_data->>'role', 'attorney'), 
    COALESCE(new.raw_user_meta_data->>'escritorio_id', 'default'),
    new.raw_user_meta_data->>'full_name'
  )
  ON CONFLICT (id) DO UPDATE
  SET email = EXCLUDED.email,
      role = EXCLUDED.role;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
