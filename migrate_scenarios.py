#!/usr/bin/env python3
"""
Migration Script: Export all scenarios from family_scenarios.json to individual files
This creates one JSON file per scenario that you can upload to the cloud app.
"""

import json
import os
from pathlib import Path

def migrate_scenarios():
    """Export all scenarios from family_scenarios.json to individual files"""

    # Input file
    input_file = "family_scenarios.json"

    # Output folder
    output_folder = Path("exported_scenarios")
    output_folder.mkdir(exist_ok=True)

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ ERROR: {input_file} not found!")
        print(f"   Looking in: {os.getcwd()}")
        return

    # Load scenarios
    print(f"📂 Loading scenarios from {input_file}...")
    try:
        with open(input_file, 'r') as f:
            scenarios = json.load(f)
    except Exception as e:
        print(f"❌ ERROR loading file: {e}")
        return

    if not isinstance(scenarios, dict):
        print(f"❌ ERROR: Invalid format in {input_file}")
        return

    # Export each scenario
    print(f"\n✅ Found {len(scenarios)} scenarios")
    print(f"📁 Exporting to folder: {output_folder.absolute()}\n")

    exported_count = 0
    for scenario_name, scenario_data in scenarios.items():
        # Clean filename (remove invalid characters)
        clean_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '-', '_', '(', ')')).strip()
        clean_name = clean_name.replace(' ', '-')

        # Create filename
        output_file = output_folder / f"{clean_name}.json"

        # Write scenario to file
        try:
            with open(output_file, 'w') as f:
                json.dump(scenario_data, f, indent=2)
            print(f"✅ Exported: {scenario_name}")
            print(f"   → {output_file.name}")
            exported_count += 1
        except Exception as e:
            print(f"❌ FAILED: {scenario_name} - {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ MIGRATION COMPLETE!")
    print(f"{'='*60}")
    print(f"📊 Exported: {exported_count} / {len(scenarios)} scenarios")
    print(f"📁 Location: {output_folder.absolute()}")
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Open the 'exported_scenarios' folder")
    print(f"   2. Find the scenario(s) you want to use")
    print(f"   3. Upload them in the Streamlit app sidebar")
    print(f"   4. Use 'Download Scenario' to save changes\n")


if __name__ == "__main__":
    print("="*60)
    print("SCENARIO MIGRATION TOOL")
    print("="*60)
    print("This script exports scenarios from family_scenarios.json")
    print("to individual JSON files for cloud upload.\n")

    migrate_scenarios()
