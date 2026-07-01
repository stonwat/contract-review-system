"""创建管理员账号脚本。

用法：
    python -m app.scripts.create_admin --username admin --password <password>
"""

import argparse
import asyncio

import bcrypt
from sqlalchemy import select

from app.db.database import async_session_factory
from app.models.admin import Admin


async def create_admin(username: str, password: str, display_name: str | None) -> None:
    async with async_session_factory() as db:
        existing = await db.execute(select(Admin).where(Admin.username == username))
        if existing.scalar_one_or_none():
            print(f"管理员 {username} 已存在")
            return

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        admin = Admin(
            username=username,
            password_hash=password_hash,
            display_name=display_name,
        )
        db.add(admin)
        await db.commit()
        print(f"管理员 {username} 创建成功")


def main() -> None:
    parser = argparse.ArgumentParser(description="创建管理员账号")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--display-name", default=None)
    args = parser.parse_args()
    asyncio.run(create_admin(args.username, args.password, args.display_name))


if __name__ == "__main__":
    main()
