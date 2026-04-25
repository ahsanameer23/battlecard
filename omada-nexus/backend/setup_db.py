import os
import asyncio
import asyncpg
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
# We will temporarily connect to the default 'postgres' database to create omada_nexus
base_url = os.getenv("DATABASE_URL")

async def setup():
    if not base_url:
        print("❌ DATABASE_URL is not set in .env")
        return
        
    # Connect to the default 'postgres' database first
    # Replace the omada_nexus database name with postgres in the URL
    admin_url = base_url.replace("/omada_nexus", "/postgres")
    
    print("Connecting to PostgreSQL server...")
    try:
        conn = await asyncpg.connect(admin_url)
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print("Please make sure your password in .env is correct and PostgreSQL is running.")
        return

    # Check if database exists
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'omada_nexus'")
    if not exists:
        print("Creating 'omada_nexus' database...")
        # We must use execute without a transaction block for CREATE DATABASE
        await conn.execute("CREATE DATABASE omada_nexus")
        print("✅ Database created.")
    else:
        print("✅ 'omada_nexus' database already exists.")
        
    await conn.close()

    print("Connecting to 'omada_nexus' to run schema...")
    # Now connect to the actual omada_nexus database to run the init.sql
    try:
        nexus_conn = await asyncpg.connect(base_url)
    except Exception as e:
        print(f"❌ Failed to connect to omada_nexus database: {e}")
        return
        
    # Read and execute init.sql
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'init.sql')
    if not os.path.exists(sql_file):
        print(f"❌ Could not find {sql_file}")
        return
        
    with open(sql_file, 'r') as f:
        schema_sql = f.read()
        
    print("Applying database schema...")
    await nexus_conn.execute(schema_sql)
    print("✅ Schema applied successfully!")
    
    await nexus_conn.close()
    print("\n🎉 Setup complete! You can now run the seed_from_excel.py script.")

if __name__ == "__main__":
    asyncio.run(setup())
