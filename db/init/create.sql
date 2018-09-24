CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    token TEXT,
    team_id TEXT,
    team_domain TEXT,
    channel_id TEXT,
    channel_name TEXT,
    slack_user_id TEXT,
    slack_user_name TEXT,
    command TEXT,
    command_text TEXT,
    response_url TEXT,
    success BOOLEAN,
    description TEXT
);

CREATE TABLE IF NOT EXISTS team_registration (
    team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    team_name TEXT,
    entry_code TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    slack_id TEXT,
    slack_name TEXT,
    team UUID
);

CREATE TABLE IF NOT EXISTS teams (
    team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    team_name TEXT,
    balance NUMERIC(10, 4)
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    origin_user_id UUID,
    destination_user_id UUID,
    amount NUMERIC(10, 4),
    description TEXT
);

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID,
    staff_function TEXT
);

CREATE TABLE IF NOT EXISTS rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    given_by UUID,
    amount NUMERIC(10, 4),
    destination TEXT,
    description TEXT
)