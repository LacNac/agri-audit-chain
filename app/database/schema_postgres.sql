CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'FARMER',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS businesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    business_name TEXT,
    business_type TEXT,
    product_type TEXT,
    tax_code TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS batches (
    id SERIAL PRIMARY KEY,
    batch_code TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    product_type TEXT,
    producer_name TEXT NOT NULL,
    origin TEXT,
    destination TEXT,
    quantity DOUBLE PRECISION,
    unit TEXT,
    production_date DATE,
    expiry_date DATE,
    status TEXT NOT NULL DEFAULT 'UNVERIFIED',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    farmer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    note TEXT,
    reason TEXT,
    return_goods BOOLEAN DEFAULT FALSE,
    rejected_at TIMESTAMP WITHOUT TIME ZONE,
    return_requested BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS samples (
    id SERIAL PRIMARY KEY,
    sample_code TEXT NOT NULL UNIQUE,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    sampling_date DATE,
    sample_quantity DOUBLE PRECISION,
    sample_unit TEXT,
    sampling_location TEXT,
    sampling_method TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_samples_one_per_batch
    ON samples(batch_id);

CREATE TABLE IF NOT EXISTS lab_reports (
    id SERIAL PRIMARY KEY,
    report_code TEXT NOT NULL UNIQUE,
    sample_id INTEGER NOT NULL REFERENCES samples(id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    lab_name TEXT,
    lab_code TEXT,
    report_date DATE,
    result TEXT,
    file_name TEXT,
    file_hash TEXT,
    file_path TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_trails (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blockchain_anchors (
    audit_id INTEGER PRIMARY KEY,
    event_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'PENDING',
    transaction_hash TEXT,
    block_number BIGINT,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    anchored_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS packages (
    id SERIAL PRIMARY KEY,
    package_code TEXT NOT NULL UNIQUE,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    quantity DOUBLE PRECISION,
    unit TEXT,
    qr_code TEXT,
    trace_id TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trace_records (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    package_id INTEGER REFERENCES packages(id) ON DELETE SET NULL,
    trace_id TEXT NOT NULL,
    public_url TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS integrity_proofs (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL UNIQUE REFERENCES lab_reports(id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    file_hash TEXT NOT NULL,
    previous_proof TEXT,
    proof_hash TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    recipient_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipient_role TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
    id SERIAL PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP WITHOUT TIME ZONE,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);
