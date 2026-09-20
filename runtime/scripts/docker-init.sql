-- Local development only. Production roles and secrets must be provisioned separately.
CREATE ROLE ams_app LOGIN PASSWORD 'ams_local_only' NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
