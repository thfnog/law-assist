-- ========================================================
-- LAW ASSIST AI - SUPABASE SCHEMA (FULL MIGRATION)
-- ========================================================

-- 1. Enable Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Escritório Table (The Tenant)
CREATE TABLE IF NOT EXISTS public.escritorio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free', -- free, pro, enterprise
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.client (
    id SERIAL PRIMARY KEY,
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id),
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
CREATE INDEX IF NOT EXISTS idx_client_escritorio ON public.client(escritorio_id);

CREATE TABLE IF NOT EXISTS public.lead (
    id SERIAL PRIMARY KEY,
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id),
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    legal_area TEXT,
    urgency TEXT DEFAULT 'medium',
    summary TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lead_phone ON public.lead(phone);
CREATE INDEX IF NOT EXISTS idx_lead_escritorio ON public.lead(escritorio_id);

CREATE TABLE IF NOT EXISTS public.transaction (
    id SERIAL PRIMARY KEY,
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id),
    client_id INTEGER REFERENCES public.client(id),
    lead_id INTEGER REFERENCES public.lead(id),
    type TEXT NOT NULL, -- 'income', 'expense'
    category TEXT NOT NULL, -- 'honorarios', 'custas', 'outros'
    amount DOUBLE PRECISION NOT NULL,
    description TEXT,
    date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_transaction_escritorio ON public.transaction(escritorio_id);

CREATE TABLE IF NOT EXISTS public.user (
    id UUID PRIMARY KEY, -- Matches Supabase Auth User ID
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'advogado', -- dono, financeiro, advogado, atendente
    escritorio_id UUID REFERENCES public.escritorio(id),
    whatsapp_instance TEXT, -- Per-user Evolution API instance
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.knowledgechunk (
    id SERIAL PRIMARY KEY,
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- Match OpenAI text-embedding-3-small
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_escritorio ON public.knowledgechunk(escritorio_id);

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

-- 8. Row Level Security (RLS)
ALTER TABLE public.client ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lead ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledgechunk ENABLE ROW LEVEL SECURITY;

-- 9. Policies (Isolate data by escritorio_id)
-- Only allow access if the user belongs to the same escritorio_id

CREATE POLICY "Access by office" ON public.client
    FOR ALL USING (escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid()));

CREATE POLICY "Access by office" ON public.lead
    FOR ALL USING (escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid()));

CREATE POLICY "Access by office" ON public.transaction
    FOR ALL USING (
        escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid())
        AND (
            (SELECT role FROM public.user WHERE id = auth.uid()) IN ('dono', 'financeiro')
        )
    );

CREATE POLICY "Access by office" ON public.knowledgechunk
    FOR ALL USING (escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid()));

CREATE POLICY "Self access" ON public.user
    FOR ALL USING (id = auth.uid());
