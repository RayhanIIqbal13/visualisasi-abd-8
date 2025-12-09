import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
json_file = PROJECT_ROOT / "Data" / "Json_Bersih" / "world_happiness_2024.json"

with open(json_file) as f:
    data = json.load(f)
    if len(data) > 0:
        entry = data[0]
        fields = list(entry.keys())
        print("Fields in entry:", fields)
        print("\nField count:", len(fields))
        
        # Check if Country or Regional indicator exist
        if "Country" in fields:
            print("WARNING: 'Country' field still exists!")
        if "Regional indicator" in fields:
            print("WARNING: 'Regional indicator' field still exists!")
        
        print("\nFirst entry:")
        print(json.dumps(entry, indent=2))
        
        # Show dystopia values for multiple entries
        print("\n" + "="*60)
        print("Sample dystopia_residual values:")
        print("="*60)
        for i in range(min(10, len(data))):
            e = data[i]
            print(f"{e['country_name']:20} (rank {e['ranking']:3}): {e['dystopia_residual']}")
