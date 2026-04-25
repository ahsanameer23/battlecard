import os
import sys
import json
import asyncio
import pandas as pd
import asyncpg
from dotenv import load_dotenv
import httpx

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("Error: DATABASE_URL not found in environment.")
    sys.exit(1)

# Ensure httpx timeout is long enough for local LLM inference
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

PROMPT_TEMPLATE = """You are a network hardware spec extraction AI. 
I am providing you with the column values for a specific network hardware product extracted from a competitive analysis spreadsheet.
The spreadsheet columns map features to product values.

Your goal is to extract the following information and output strict JSON matching this schema:
{{
  "vendor": "<Extract vendor from model name or assume from context. e.g. TP-Link, Cisco, Ruijie, Hikvision. For models like RG-ES... it's Ruijie, DS-3E... is Hikvision, ES/SG... without vendor prefix are likely Omada/TP-Link.>",
  "model": "<The model name exactly as specified>",
  "price_usd": <Float price if found, otherwise null. Only look for dollar amounts.>,
  "specs_json": {{
    "quantitative": {{
      "total_ports": <integer, sum of all ports. if not found try to guess from model name or leave null>,
      "poe_budget_w": <integer watts, e.g. 54 for 54W>,
      "uplink_speed_gbps": <integer gbps>,
      "poe_ports": <integer>,
      "switching_capacity_gbps": <number>,
      "max_power_consumption_w": <number>
    }},
    "boolean_features": {{
      "l2_plus_routing": <boolean>,
      "fanless": <boolean, if fanless is indicated or implied>
    }},
    "misc": {{
      "form_factor": "<string, e.g. Desktop, Wall-Mounting, Rackmount>"
    }}
  }}
}}

--- INPUT DATA ---
Model Column Name: {model_name}
Category: {category}
Subcategory: {subcategory}
Tier: {tier}

Row Values:
{row_values}
"""

async def process_model(conn, model_name, category, subcategory, tier, row_values):
    prompt = PROMPT_TEMPLATE.format(
        model_name=model_name,
        category=category,
        subcategory=subcategory,
        tier=tier,
        row_values=row_values
    )
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            data = json.loads(result.get("response", "{}"))
        
        vendor = data.get("vendor", "Unknown")
        model = data.get("model", model_name)
        price_usd = data.get("price_usd")
        specs_json = data.get("specs_json", {})
        
        # Calculate completeness
        q_fields = specs_json.get("quantitative", {})
        completeness = round(sum(1 for v in q_fields.values() if v is not None) / (len(q_fields) or 1), 2)
        
        source = 'internal' if vendor.lower() in ['tp-link', 'omada'] else 'competitor'
        
        await conn.execute("""
            INSERT INTO omada_nexus.products (source, vendor, model, category, subcategory, tier, price_usd, specs_json, data_completeness)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9)
            ON CONFLICT (vendor, model) DO UPDATE SET 
                specs_json = EXCLUDED.specs_json, 
                price_usd = EXCLUDED.price_usd,
                data_completeness = EXCLUDED.data_completeness,
                subcategory = EXCLUDED.subcategory,
                category = EXCLUDED.category,
                tier = EXCLUDED.tier
        """, source, vendor, model, category, subcategory, tier, price_usd, json.dumps(specs_json), completeness)
        
        print(f"✅ Upserted {source} {vendor} {model}")
        
    except Exception as e:
        print(f"❌ Failed to process {model_name}: {str(e)}")

async def process_file(conn, filepath):
    filename = os.path.basename(filepath)
    print(f"\nProcessing File: {filename}")
    
    category = "Unknown"
    if "Switch" in filename:
        category = "Switches"
    elif "Wireless" in filename:
        category = "Wireless"
        
    try:
        xls = pd.ExcelFile(filepath)
    except Exception as e:
        print(f"Error opening Excel file {filepath}: {e}")
        return

    for sheet in xls.sheet_names:
        print(f"  Reading Sheet: {sheet}")
        subcategory = sheet
        tier = "Enterprise" # Defaulting for now
        
        df = pd.read_excel(xls, sheet_name=sheet)
        if df.empty or len(df.columns) < 2:
            print(f"  Skipping empty or invalid sheet {sheet}")
            continue
            
        feature_col = df.columns[0]
        
        for model_col in df.columns[1:]:
            if pd.isna(model_col) or 'Unnamed' in str(model_col):
                continue
                
            row_values = ""
            for idx, row in df.iterrows():
                feature = str(row[feature_col]).strip()
                val = str(row[model_col]).strip()
                if feature and feature != 'nan' and val and val != 'nan':
                    row_values += f"{feature}: {val}\n"
                    
            if not row_values.strip():
                continue
                
            await process_model(conn, str(model_col), category, subcategory, tier, row_values)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python seed_from_excel.py <path_to_template_datas_dir>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    
    print("Connecting to DB...")
    conn = await asyncpg.connect(DB_URL)
    
    try:
        if os.path.isfile(target_path):
            await process_file(conn, target_path)
        else:
            for root, dirs, files in os.walk(target_path):
                for f in files:
                    if f.endswith('.xlsx') and not f.startswith('~'):
                        await process_file(conn, os.path.join(root, f))
    finally:
        await conn.close()
        print("\nFinished seeding.")

if __name__ == "__main__":
    asyncio.run(main())
