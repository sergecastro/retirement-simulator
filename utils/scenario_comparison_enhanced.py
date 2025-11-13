"""
Enhanced Scenario Comparison Engine
====================================
Enables comparing 3+ retirement scenarios simultaneously with full analytics.

Features:
- Store and manage 3+ scenarios
- Run parallel simulations
- Calculate deltas and comparisons
- Export to CSV/PDF
- Visual comparison data preparation

Author: ForeCash Development Team
Created: November 12, 2025
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class ScenarioComparisonEngine:
    """
    Manages comparison of 3+ retirement scenarios simultaneously.

    This engine handles:
    - Scenario storage and metadata
    - Parallel simulation execution
    - Delta calculations between scenarios
    - Export functionality (CSV, PDF, JSON)
    - Comparison data preparation for visualization
    """

    def __init__(self):
        """Initialize the comparison engine"""
        self.scenarios: List[Dict[str, Any]] = []
        self.comparison_results: Optional[pd.DataFrame] = None

    def add_scenario(
        self,
        name: str,
        scenario_data: Dict[str, Any],
        description: str = "",
        is_base: bool = False
    ) -> None:
        """
        Add a scenario to the comparison set.

        Args:
            name: Scenario name (e.g., "Retire at 65")
            scenario_data: Full scenario data dictionary
            description: Optional description (e.g., "Conservative plan with delayed retirement")
            is_base: Mark as base scenario for delta calculations
        """
        scenario = {
            'name': name,
            'description': description,
            'data': scenario_data,
            'simulation_results': None,
            'is_base': is_base,
            'added_at': datetime.now().isoformat()
        }

        self.scenarios.append(scenario)

    def remove_scenario(self, name: str) -> bool:
        """
        Remove a scenario from comparison set.

        Args:
            name: Scenario name to remove

        Returns:
            bool: True if removed, False if not found
        """
        original_count = len(self.scenarios)
        self.scenarios = [s for s in self.scenarios if s['name'] != name]
        return len(self.scenarios) < original_count

    def clear_scenarios(self) -> None:
        """Remove all scenarios from comparison set"""
        self.scenarios = []
        self.comparison_results = None

    def run_all_simulations(self, simulation_function, **sim_params) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for all scenarios.

        Args:
            simulation_function: Function that runs simulation (from simulation_core)
            **sim_params: Additional simulation parameters

        Returns:
            dict: Summary of simulation results
        """
        from simulation_core import run_simulation

        results_summary = {
            'scenarios_count': len(self.scenarios),
            'simulations_run': 0,
            'failed': []
        }

        for scenario in self.scenarios:
            try:
                # Extract parameters from scenario data
                data = scenario['data']

                # Run simulation
                results = run_simulation(
                    age=data.get('age', 35),
                    partner_exists=data.get('partner_exists', False),
                    partner_age=data.get('partner_age', 35),
                    total_income=data.get('total_income', 0),
                    total_expenses=data.get('total_expenses', 0),
                    combined_financial_assets=data.get('liquid_assets', 0),
                    primary_residence_value=data.get('primary_residence_value', 0),
                    secondary_residence_value=data.get('secondary_residence_value', 0),
                    combined_other_assets_total=data.get('other_assets', 0),
                    total_liabilities_local=data.get('total_liabilities', 0),
                    partner_liabilities=0,
                    tax_rate=sim_params.get('tax_rate', 0.25),
                    inflation_rate=sim_params.get('inflation_rate', 0.03),
                    investment_return_rate=sim_params.get('investment_return_rate', 0.07),
                    simulation_years=sim_params.get('simulation_years', 30),
                    mc_iterations=sim_params.get('mc_iterations', 0),
                    goal_costs={},
                    college_inflation_pct=4.0,
                    base_public_in=20000.0,
                    base_public_out=40000.0,
                    base_private=60000.0,
                    ira_balance=data.get('ira_balance', 0),
                    four01k_403b_balance=data.get('four01k_403b_balance', 0),
                    partner_ira_balance=data.get('partner_ira_balance', 0),
                    partner_four01k_403b_balance=data.get('partner_four01k_403b_balance', 0),
                    monthly_surplus=data.get('monthly_surplus', 0),
                    combined_total_liabilities=data.get('total_liabilities', 0)
                )

                scenario['simulation_results'] = results
                results_summary['simulations_run'] += 1

            except Exception as e:
                results_summary['failed'].append({
                    'scenario': scenario['name'],
                    'error': str(e)
                })

        return results_summary

    def get_comparison_table(self) -> pd.DataFrame:
        """
        Generate comparison table of key metrics across all scenarios.

        Returns:
            pd.DataFrame: Comparison table with scenarios as columns, metrics as rows
        """
        if not self.scenarios:
            return pd.DataFrame()

        # Build comparison data
        comparison_data = {}

        for scenario in self.scenarios:
            name = scenario['name']
            results = scenario.get('simulation_results')
            data = scenario['data']

            if results:
                comparison_data[name] = {
                    'Description': scenario.get('description', '-'),
                    'Age': data.get('age', '-'),
                    'Annual Income': f"${data.get('total_income', 0):,.0f}",
                    'Annual Expenses': f"${data.get('total_expenses', 0):,.0f}",
                    'Starting Liquid Assets': f"${data.get('liquid_assets', 0):,.0f}",
                    'Final Savings': f"${results.get('final_savings', 0):,.0f}",
                    'Final Net Worth': f"${results.get('final_net_worth', 0):,.0f}",
                    'Years Solvent': results.get('years_solvent', 0),
                    'Health Score': f"{results.get('health_score', 0)}/100",
                    'Monthly Surplus': f"${data.get('monthly_surplus', 0):,.0f}"
                }
            else:
                comparison_data[name] = {
                    'Description': scenario.get('description', '-'),
                    'Status': 'Simulation not run'
                }

        df = pd.DataFrame(comparison_data).T
        self.comparison_results = df

        return df

    def get_deltas_vs_base(self) -> Optional[pd.DataFrame]:
        """
        Calculate deltas for all scenarios compared to base scenario.

        Returns:
            pd.DataFrame: Delta values (or None if no base scenario)
        """
        base_scenario = next((s for s in self.scenarios if s.get('is_base')), None)

        if not base_scenario or not base_scenario.get('simulation_results'):
            return None

        base_results = base_scenario['simulation_results']
        deltas = {}

        for scenario in self.scenarios:
            if scenario == base_scenario:
                continue

            results = scenario.get('simulation_results')
            if not results:
                continue

            name = scenario['name']
            deltas[name] = {
                'vs Base Savings': results['final_savings'] - base_results['final_savings'],
                'vs Base Net Worth': results['final_net_worth'] - base_results['final_net_worth'],
                'vs Base Years': results['years_solvent'] - base_results['years_solvent'],
                'vs Base Health': results['health_score'] - base_results['health_score']
            }

        return pd.DataFrame(deltas).T if deltas else None

    def export_to_csv(self, filepath: str) -> bool:
        """
        Export comparison table to CSV file.

        Args:
            filepath: Output CSV file path

        Returns:
            bool: Success status
        """
        try:
            if self.comparison_results is None:
                self.get_comparison_table()

            if self.comparison_results is not None:
                self.comparison_results.to_csv(filepath)
                return True
            return False
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False

    def export_to_json(self, filepath: str) -> bool:
        """
        Export all scenario data to JSON file.

        Args:
            filepath: Output JSON file path

        Returns:
            bool: Success status
        """
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'scenarios_count': len(self.scenarios),
                'scenarios': [
                    {
                        'name': s['name'],
                        'description': s['description'],
                        'data': s['data'],
                        'has_results': s['simulation_results'] is not None
                    }
                    for s in self.scenarios
                ]
            }

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

            return True
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False

    def export_to_pdf(self, filepath: str) -> bool:
        """
        Export comparison to PDF file (requires reportlab).

        Args:
            filepath: Output PDF file path

        Returns:
            bool: Success status
        """
        # TODO: Implement PDF export using reportlab
        # For Phase 3 implementation
        print("PDF export will be implemented in Phase 3")
        return False

    def get_scenario_count(self) -> int:
        """Get number of scenarios in comparison set"""
        return len(self.scenarios)

    def get_scenario_names(self) -> List[str]:
        """Get list of all scenario names"""
        return [s['name'] for s in self.scenarios]

    def has_simulation_results(self) -> bool:
        """Check if all scenarios have simulation results"""
        return all(s.get('simulation_results') is not None for s in self.scenarios)
