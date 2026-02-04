# test_pg.py
import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="Gbenga12@#12",
    host="db.bvmgydhrvufwubjecmzm.supabase.co",
    port="5432"
)
print(conn.status)  # 1 means connection is OK
conn.close()
