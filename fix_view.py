#!/usr/bin/env python
import psycopg2

try:
    conn = psycopg2.connect(database='mydb_clinic', user='odoo', password='987654321aA', host='localhost', client_encoding='UTF8')
    cursor = conn.cursor()
    # Delete the problematic view
    cursor.execute("DELETE FROM ir_ui_view WHERE name = 'clinic.reception.form'")
    conn.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    conn.close()
    print(f'Deleted {deleted_rows} view(s) successfully')
except Exception as e:
    print(f'Error: {e}')
    import sys
    sys.exit(1)
