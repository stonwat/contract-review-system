import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432,
    dbname='contract_review', user='app', password='apppassword'
)
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name='admins'
    ORDER BY ordinal_position
""")
print("=== admins 表结构 ===")
for row in cur.fetchall():
    print(f"  {row[0]:20s} {row[1]:15s} nullable={row[2]:5s} default={row[3]}")

cur.execute("""
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'admins'::regclass
""")
print("\n=== 现有约束 ===")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
