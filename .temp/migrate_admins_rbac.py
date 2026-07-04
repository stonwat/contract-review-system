"""DDL migration: add role/city columns and CHECK constraints to admins table"""
import subprocess
import sys

SQL = """
-- 1. Add role column with default 'viewer'
ALTER TABLE admins ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'viewer';

-- 2. Add city column (nullable)
ALTER TABLE admins ADD COLUMN IF NOT EXISTS city VARCHAR(20);

-- 3. Add CHECK constraints (drop if exist first to allow re-run)
ALTER TABLE admins DROP CONSTRAINT IF EXISTS ck_admins_role;
ALTER TABLE admins ADD CONSTRAINT ck_admins_role CHECK (role IN ('super_admin', 'city_admin', 'viewer'));

ALTER TABLE admins DROP CONSTRAINT IF EXISTS ck_admins_city_required;
ALTER TABLE admins ADD CONSTRAINT ck_admins_city_required CHECK (
  role <> 'city_admin' OR city IS NOT NULL
);

ALTER TABLE admins DROP CONSTRAINT IF EXISTS ck_admins_city_null;
ALTER TABLE admins ADD CONSTRAINT ck_admins_city_null CHECK (
  role = 'city_admin' OR city IS NULL
);

-- 4. Update existing admin to super_admin
UPDATE admins SET role = 'super_admin' WHERE username = 'admin' AND role = 'viewer';
"""

env = {"PGPASSWORD": "apppassword"}
result = subprocess.run(
    [r"C:\PostgreSQL\bin\psql.exe", "-U", "app", "-h", "localhost", "-d", "contract_review", "-c", SQL],
    env={**__import__('os').environ, **env},
    capture_output=True, text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

if result.returncode == 0:
    print("\n=== 迁移完成，验证表结构 ===")
    subprocess.run(
        [r"C:\PostgreSQL\bin\psql.exe", "-U", "app", "-h", "localhost", "-d", "contract_review", "-c",
         "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name='admins' ORDER BY ordinal_position"],
        env={**__import__('os').environ, **env}
    )
    subprocess.run(
        [r"C:\PostgreSQL\bin\psql.exe", "-U", "app", "-h", "localhost", "-d", "contract_review", "-c",
         "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'admins'::regclass"],
        env={**__import__('os').environ, **env}
    )
    subprocess.run(
        [r"C:\PostgreSQL\bin\psql.exe", "-U", "app", "-h", "localhost", "-d", "contract_review", "-c",
         "SELECT id, username, role, city, is_active FROM admins"],
        env={**__import__('os').environ, **env}
    )
