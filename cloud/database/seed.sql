-- ChildGuard Local Sandbox Seed Data
-- Creates sample parent, supervised child device, safe zones, and restricted danger zones.

-- 1. Insert Sample Parent (Aditi Sharma)
INSERT INTO parents (id, full_name, email, phone_number, password_hash)
VALUES (
    'a1111111-1111-1111-1111-111111111111',
    'Aditi Sharma',
    'aditi.parent@example.com',
    '+919876543210',
    -- bcrypt hash for demo password
    '$2a$12$e86g9PqKzT1bI8qJ2P1L.eYvD3B7q0kFf9P6V2kQ8a3B5C7D9E0F.'
) ON CONFLICT (email) DO NOTHING;

-- 2. Insert Supervised Child Device (Aarav, age 11, matching default device ID: child_dev_99182)
INSERT INTO children (id, parent_id, device_uid, first_name, age_years)
VALUES (
    'b2222222-2222-2222-2222-222222222222',
    'a1111111-1111-1111-1111-111111111111',
    'child_dev_99182',
    'Aarav',
    11
) ON CONFLICT (device_uid) DO NOTHING;

-- 3. Insert Safe Zone: "Delhi Public School & Campus"
-- Polygon around sample coordinates (Longitudes ~77.2090 to 77.2150, Latitudes ~28.6130 to 28.6180)
INSERT INTO geofences (child_id, zone_name, is_safe_zone, boundary)
VALUES (
    'b2222222-2222-2222-2222-222222222222',
    'Delhi Public School Campus (Safe Zone)',
    TRUE,
    ST_GeomFromText(
        'POLYGON((
            77.2090 28.6130,
            77.2150 28.6130,
            77.2150 28.6180,
            77.2090 28.6180,
            77.2090 28.6130
        ))', 
        4326
    )
);

-- 4. Insert Safe Zone: "Home & Neighborhood Park"
INSERT INTO geofences (child_id, zone_name, is_safe_zone, boundary)
VALUES (
    'b2222222-2222-2222-2222-222222222222',
    'Home Neighborhood (Safe Zone)',
    TRUE,
    ST_GeomFromText(
        'POLYGON((
            77.2200 28.6200,
            77.2260 28.6200,
            77.2260 28.6250,
            77.2200 28.6250,
            77.2200 28.6200
        ))', 
        4326
    )
);

-- 5. Insert Danger Zone: "Industrial Construction Yard & Riverbank"
INSERT INTO geofences (child_id, zone_name, is_safe_zone, boundary)
VALUES (
    'b2222222-2222-2222-2222-222222222222',
    'Industrial Construction Site (Danger Zone)',
    FALSE,
    ST_GeomFromText(
        'POLYGON((
            77.2300 28.6100,
            77.2380 28.6100,
            77.2380 28.6150,
            77.2300 28.6150,
            77.2300 28.6100
        ))', 
        4326
    )
);
