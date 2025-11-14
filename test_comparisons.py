"""Quick test of comparison scenarios storage"""
import sys
from utils.comparison_scenarios import save_comparison_scenario, list_comparison_scenarios

# Try to save a test comparison
try:
    print("[TEST] Starting comparison storage test...")

    comp_id = save_comparison_scenario(
        base_plan_id="test_plan_123",
        name="Test Comparison",
        description="Testing storage",
        adjustments={
            "adjusted_income": 50000,
            "adjusted_expenses": 30000,
            "adjusted_return_rate": 0.07,
            "adjusted_inflation_rate": 0.03
        }
    )
    print(f"✅ SUCCESS: Saved comparison with ID: {comp_id}")

    # Try to list
    all_comps = list_comparison_scenarios()
    print(f"✅ Total comparisons in storage: {len(all_comps)}")

    for comp in all_comps:
        print(f"  - {comp.get('name')} (ID: {comp.get('id')})")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
