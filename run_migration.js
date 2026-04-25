const { Client } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: 'omada-nexus/.env' });

async function migrate() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL
  });
  
  try {
    await client.connect();
    const sql = fs.readFileSync(path.join(__dirname, 'omada-nexus', 'database', 'add_temp_weight_function.sql'), 'utf8');
    await client.query(sql);
    console.log("✅ Successfully deployed the temporary weight function to PostgreSQL!");
  } catch (err) {
    console.error("❌ Migration failed:", err);
  } finally {
    await client.end();
  }
}

migrate();
