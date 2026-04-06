#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres --dbname "${DB_NAME:-main_db}" \
    -v db_name="${DB_NAME:-main_db}" \
    -v db_user="$DB_USER" \
    -v db_password="$DB_PASSWORD" \
    -v ro_password="$READONLY_PASSWORD" <<-EOSQL

    SELECT format('CREATE USER %I WITH PASSWORD %L', :'db_user', :'db_password') \gexec
    SELECT format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', :'db_name', :'db_user') \gexec
    SELECT format('CREATE USER readonly_user WITH PASSWORD %L', :'ro_password') \gexec
    SELECT format('GRANT CONNECT ON DATABASE %I TO readonly_user', :'db_name') \gexec

    GRANT USAGE ON SCHEMA public TO :"db_user";
    GRANT ALL ON ALL TABLES IN SCHEMA public TO :"db_user";
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO :"db_user";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO :"db_user";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO :"db_user";

    GRANT USAGE ON SCHEMA public TO readonly_user;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO readonly_user;
EOSQL
