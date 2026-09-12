-- ChildGuard Cloud Database Schema
-- PostGIS Spatial Extension & Privacy-Compliant Data Retention

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE parents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(128) NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    phone_number VARCHAR(32) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    device_uid VARCHAR(128) UNIQUE NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    age_years INT NOT NULL CHECK (age_years <= 18),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE geofences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    zone_name VARCHAR(64) NOT NULL,
    is_safe_zone BOOLEAN DEFAULT TRUE,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_geofences_spatial ON geofences USING GIST(boundary);

CREATE TABLE location_history (
    id BIGSERIAL PRIMARY KEY,
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    location GEOMETRY(Point, 4326) NOT NULL,
    speed FLOAT DEFAULT 0.0,
    recorded_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_location_history_coords ON location_history USING GIST(location);
CREATE INDEX idx_location_child_time ON location_history(child_id, recorded_at DESC);

CREATE TABLE security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    alert_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    payload JSONB NOT NULL,
    acknowledged_by_parent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_alerts_child ON security_alerts(child_id, acknowledged_by_parent);
