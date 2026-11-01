"""
Seed for Render deployment — runs during build command.
Idempotent: skips if data already exists.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main() -> None:
    from src.database.seed import seed_roles_and_admin

    try:
        await seed_roles_and_admin()
        print("Seed completed: roles + admin created (or already exist).")
    except Exception as e:
        print(f"Seed skipped or failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
