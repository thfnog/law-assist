-- ========================================================
-- CENTRALIZATION MIGRATION: Internal Kanban & Storage
-- ========================================================

-- 1. Files Table (Replaces Google Drive)
CREATE TABLE IF NOT EXISTS public.file (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id),
    client_id INTEGER REFERENCES public.client(id),
    name TEXT NOT NULL,
    storage_path TEXT NOT NULL, -- Path in Supabase Storage
    file_type TEXT,
    size INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Update Client statuses for Kanban
-- Typical Legal Kanban: lead, triagem, peticao_inicial, em_andamento, concluso, arquivado
ALTER TABLE public.client DROP COLUMN IF EXISTS status;
ALTER TABLE public.client ADD COLUMN status TEXT DEFAULT 'triagem';

-- 3. Enable RLS
ALTER TABLE public.file ENABLE ROW LEVEL SECURITY;

-- 4. Policies
CREATE POLICY "Access files by office" ON public.file
    FOR ALL USING (escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid()));

-- 5. Storage Buckets (Note: Bucket creation is usually done via API or Dashboard, but policies are SQL)
-- To be run in the SQL editor:
-- INSERT INTO storage.buckets (id, name) VALUES ('documents', 'documents');
-- CREATE POLICY "Office access to storage" ON storage.objects ...
