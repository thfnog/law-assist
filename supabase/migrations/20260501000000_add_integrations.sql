-- =============================================
-- Migration: Add Escritório Integrations
-- Date: 2026-05-01
-- Description: Creates a table to store integration tokens and configs (OAuth, etc.)
-- =============================================

CREATE TABLE IF NOT EXISTS public.escritorio_integracao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    escritorio_id UUID NOT NULL REFERENCES public.escritorio(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google_drive', 'trello', etc.
    config JSONB NOT NULL DEFAULT '{}'::jsonb, -- stores access_token, refresh_token, token_expiry, client_id, etc.
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(escritorio_id, provider)
);

-- RLS
ALTER TABLE public.escritorio_integracao ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Access by office" ON public.escritorio_integracao
    FOR ALL USING (escritorio_id = (SELECT escritorio_id FROM public.user WHERE id = auth.uid()));
