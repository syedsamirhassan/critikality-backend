-- Workers indexes
CREATE INDEX IF NOT EXISTS idx_workers_client_company ON workers(client_company_id);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);
CREATE INDEX IF NOT EXISTS idx_workers_email ON workers(email);
CREATE INDEX IF NOT EXISTS idx_workers_employee_id ON workers(employee_id);
CREATE INDEX IF NOT EXISTS idx_workers_created_at ON workers(created_at DESC);

-- Devices indexes
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_ip ON devices(ip_address);
CREATE INDEX IF NOT EXISTS idx_devices_created_at ON devices(created_at DESC);

-- Zones indexes
CREATE INDEX IF NOT EXISTS idx_zones_type ON location_zones(zone_type);
CREATE INDEX IF NOT EXISTS idx_zones_status ON location_zones(status);
CREATE INDEX IF NOT EXISTS idx_zones_created_at ON location_zones(created_at DESC);

-- Scan events indexes
CREATE INDEX IF NOT EXISTS idx_scan_events_worker ON scan_events(worker_id);
CREATE INDEX IF NOT EXISTS idx_scan_events_device ON scan_events(device_id);
CREATE INDEX IF NOT EXISTS idx_scan_events_zone ON scan_events(zone_id);
CREATE INDEX IF NOT EXISTS idx_scan_events_timestamp ON scan_events(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_events_direction ON scan_events(direction);

-- Emergency events indexes
CREATE INDEX IF NOT EXISTS idx_emergency_status ON emergency_events(status);
CREATE INDEX IF NOT EXISTS idx_emergency_type ON emergency_events(event_type);
CREATE INDEX IF NOT EXISTS idx_emergency_created ON emergency_events(created_at DESC);

-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_company ON user_profiles(client_company_id);

-- User roles indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_company ON user_roles(client_company_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role);
