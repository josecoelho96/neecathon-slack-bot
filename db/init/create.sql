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

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    slack_id TEXT,
    slack_name TEXT,
    user_id UUID,
    team UUID,
    name TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    team_id UUID,
    team_name TEXT,
    balance NUMERIC(10, 4)
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    origin_user_id UUID,
    destination_user_id UUID,
    amount NUMERIC(10, 4),
    description TEXT
);