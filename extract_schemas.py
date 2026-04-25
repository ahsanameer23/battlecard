import os
import json
import pandas as pd
import re

TEMPLATE_DIR = r"c:\Ameer\MyApp\Battlecard\omada-nexus\Template-datas"
OUTPUT_FILE = r"c:\Ameer\MyApp\Battlecard\src\ai\schemas-registry.json"

registry = {}

def sanitize_key(key):
    # Convert feature name to a safe JSON/Zod key format
    k = str(key).strip().lower()
    k = re.sub(r'[^a-z0-9_]', '_', k)
    k = re.sub(r'_+', '_', k)
    return k.strip('_')

def infer_type(key_name):
    k = key_name.lower()
    
    # Heuristic for arrays
    if any(x in k for x in ['features', 'modes', 'protocols', 'list', 'standards']):
        return "array"
        
    # Heuristic for booleans
    if any(x in k for x in ['support', 'managed', 'fanless', 'poe', 'yes', 'no', '?']):
        return "boolean"
        
    # Heuristic for numbers
    if any(x in k for x in ['speed', 'mbps', 'port', 'budget', 'capacity', 'price', 'weight', 'dimensions', 'count', 'rate', 'power', 'v', 'w', 'ghz', 'mhz', 'gb', 'mb', 'tb']):
        return "number"
        
    return "string"

for root, dirs, files in os.walk(TEMPLATE_DIR):
    for f in files:
        if f.endswith('.xlsx') and not f.startswith('~'):
            filepath = os.path.join(root, f)
            category_name = f.replace('.xlsx', '')
            
            try:
                xls = pd.ExcelFile(filepath)
                # Take the first sheet as representative for the schema
                df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
                if df.empty or len(df.columns) < 2:
                    continue
                
                # First column is the features
                features = df.iloc[:,0].dropna().tolist()
                
                schema_fields = {}
                for feat in features:
                    feat_str = str(feat).strip()
                    if feat_str and feat_str.lower() != 'nan':
                        key = sanitize_key(feat_str)
                        schema_fields[key] = {
                            "label": feat_str,
                            "type": infer_type(key)
                        }
                
                if schema_fields:
                    registry[category_name] = schema_fields
                    print(f"Extracted {len(schema_fields)} fields from {category_name}")
                    
            except Exception as e:
                print(f"Error processing {f}: {e}")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2)

print(f"\nRegistry saved to {OUTPUT_FILE}")
