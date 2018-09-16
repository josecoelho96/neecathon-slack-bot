CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    token TEXT,
    team_id TEXT,
    team_domain TEXT,
    channel_id TEXT,
    channel_name TEXT,
    user_id TEXT,
    user_name TEXT,
    command TEXT,
    command_text TEXT,
    response_url TEXT,
    success BOOLEAN,
    description TEXT
);

CREATE TABLE IF NOT EXISTS team_registration (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    team_id UUID,
    team_name TEXT,
    entry_code TEXT
);