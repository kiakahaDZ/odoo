#!/bin/bash

set -e

# Wait for database to be ready
echo "Waiting for database to be ready at $DB_HOST:$DB_PORT..."
while ! python3 -c "import psycopg2; psycopg2.connect(host='$DB_HOST', port='$DB_PORT', user='$DB_USER', password='$DB_PASSWORD', dbname='$DB_NAME')" 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

# Define the path for the modified config
CONFIG_FILE="/etc/odoo/odoo.conf"
TMP_CONFIG="/tmp/odoo.conf"

# Copy the original config to a temporary location to avoid "Device or resource busy"
# (which happens when sed tries to modify a mounted file directly)
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$TMP_CONFIG"
    
    # Update tmp config with environment variables
    sed -i "s/^db_host = .*/db_host = $DB_HOST/" "$TMP_CONFIG"
    sed -i "s/^db_port = .*/db_port = $DB_PORT/" "$TMP_CONFIG"
    sed -i "s/^db_user = .*/db_user = $DB_USER/" "$TMP_CONFIG"
    sed -i "s/^db_password = .*/db_password = $DB_PASSWORD/" "$TMP_CONFIG"
    sed -i "s/^db_name = .*/db_name = $DB_NAME/" "$TMP_CONFIG"
    sed -i "s/^admin_passwd = .*/admin_passwd = ${ODOO_ADMIN_PASSWORD:-admin}/" "$TMP_CONFIG"
    sed -i "s/^http_port = .*/http_port = ${ODOO_HTTP_PORT:-8069}/" "$TMP_CONFIG"
    
    # Update addons path to a standard container path
    sed -i "s|^addons_path = .*|addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons|" "$TMP_CONFIG"
    
    FINAL_CONFIG="$TMP_CONFIG"
else
    FINAL_CONFIG="$CONFIG_FILE"
fi

# If the first argument is 'odoo', we use the final config file
if [ "$1" = 'odoo' ]; then
    shift
    exec odoo -c "$FINAL_CONFIG" "$@"
fi

exec "$@"