import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv('omada-nexus/.env')

async def run_migration():
    db_url = os.getenv("DATABASE_URL")
    print(f"Connecting to {db_url}...")
    conn = await asyncpg.connect(db_url)
    
    with open('omada-nexus/database/add_temp_weight_function.sql', 'r') as f:
        sql = f.read()
        
    print("Executing SQL migration...")
    await conn.execute(sql)
    print("Migration successful!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
