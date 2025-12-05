-- Aktiver pgvector utvidelsen (Krever ankane/pgvector image)
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Tabell for KLIENT-data (API Nøkler)
-- Brukes av /register_key og /analyze
CREATE TABLE IF NOT EXISTS user_api_keys (
    user_id VARCHAR(50) PRIMARY KEY,       -- Slack/Discord User ID
    api_key VARCHAR(255) NOT NULL,         -- Klientens unike API nøkkel (for kilde-API)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabell for DATTERENS/Personlig Kontekst (RAG)
-- Brukes av /store_context og /explain_context
CREATE TABLE IF NOT EXISTS user_contexts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,          -- For å segmentere konteksten per bruker
    original_text TEXT NOT NULL,           -- Den originale teksten brukeren ga
    embedding VECTOR(1536) NOT NULL,       -- Vektor (1536 dimensjoner for OpenAI Ada)
    metadata JSONB,                        -- F.eks. kilde: Discord, tone, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_contexts_embedding ON user_contexts USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 3. Tabell for EKSPERT-DATA (Moats/Finetuning)
-- Brukes av /store_moat_data (fremtidig)
CREATE TABLE IF NOT EXISTS moat_datasets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    moat_type VARCHAR(50) NOT NULL,
    moat_description TEXT NOT NULL,
    confidence_score NUMERIC(5, 2),
    date_recorded TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabell for ETISK SAMTYKKE (Opt-In)
-- Brukes for å sjekke om data kan brukes til global modelltrening
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id VARCHAR(50) PRIMARY KEY,
    allow_training BOOLEAN DEFAULT FALSE,  -- TRUE betyr at anonymisert data kan brukes til Finetuning
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
