# monte_carlo.py - Monte Carlo simulation (fixed operand error)
import pandas as pd
import numpy as np
from financial_utils import safe_float

def run_simple_monte_carlo(financial_data, sim_params, family_cashflows):
    iterations = sim_params['mc_iterations']
    years = sim_params['simulation_years']
    
    mc_df = pd.DataFrame(index=range(years), columns=range(iterations))
    
    for i in range(iterations):
        savings = safe_float(financial_data['liquid_assets'])
        savings_path = [savings]
        
        for y in range(1, years):
            return_rate = np.random.normal(sim_params['investment_return_rate']/100, 0.02)
            inflation = np.random.normal(sim_params['inflation_rate']/100, 0.01)
            
            # total_income / total_expenses are MONTHLY — ×12 to annualize so the
            # per-year flow matches the annual portfolio growth applied below.
            income = financial_data['total_income'] * 12 * (1 + inflation)
            expenses = financial_data['total_expenses'] * 12 * (1 + inflation)
            
            flow = income - expenses + safe_float(family_cashflows.get(y, {}).get('inflow_delta', 0)) - safe_float(family_cashflows.get(y, {}).get('expense_delta', 0))
            
            savings = savings * (1 + return_rate) + flow
            savings_path.append(savings)
        
        mc_df[i] = savings_path
    
    success_rate = (mc_df.iloc[-1] > 0).mean() * 100
    
    return {
        'mc_df': mc_df,
        'success_rate': success_rate
    }