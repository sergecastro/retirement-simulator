# Embedded default scenarios
import math
nan = math.nan  # Handle NaN values in data

EMBEDDED_SCENARIOS = {
    'ORIGINAL_70+_RETIREMENT_SCENARIO': {
        # === USER INFO (GENERIC) ===
        'user_name': 'John Smith',
        'age': 65,
        'partner_exists': True,
        'partner_name': 'Jane Smith',
        'partner_age': 63,
        'age_group': '70+',
        'IS_TRUSTED_USER': False,

        # === INCOME (MINIMAL - ONLY 3 VALUES) ===
        'salary_wages': 50000.0,
        'social_security_income': 2500.0,
        'rental_income': 1000.0,
        'pension_income': 0.0,
        'self_employment_income': 0.0,
        'investment_income': 0.0,
        'other_income': 0.0,
        'total_income': 53500.0,

        # === EXPENSES (MINIMAL - ONLY 5 VALUES) ===
        'housing_expenses': 1500.0,
        'utilities_expenses': 300.0,
        'groceries_expenses': 600.0,
        'healthcare_expenses': 400.0,
        'property_tax_expenses': 400.0,
        'transportation_expenses': 0.0,
        'entertainment_expenses': 0.0,
        'restaurant_expenses': 0.0,
        'travel_expenses': 0.0,
        'insurance_expenses': 0.0,
        'education_expenses': 0.0,
        'childcare_expenses': 0.0,
        'clothing_expenses': 0.0,
        'charitable_donations': 0.0,
        'miscellaneous_expenses': 0.0,
        'other_expenses': 0.0,
        'total_expenses': 3200.0,

        # === ASSETS (MINIMAL - ONLY 3 VALUES) ===
        'ira_balance': 300000.0,
        'four01k_403b_balance': 200000.0,
        'primary_residence_value': 400000.0,
        'partner_ira_balance': 150000.0,
        'partner_four01k_403b_balance': 100000.0,
        'partner_four01k_balance': 0,
        'taxable_investment_accounts': 0.0,
        'high_yield_savings_account': 0.0,
        'hsa_balance': 0.0,
        'five29_plan_balance': 0.0,
        'secondary_residence_value': 0.0,
        'vehicles_value': 0.0,
        'jewelry_collectibles_value': 0.0,
        'business_ownership_value': 0.0,
        'cryptocurrency_holdings': 0.0,
        'other_assets': 0.0,
        'pension_fund_value': 0.0,
        'life_insurance_cash_value': 0.0,
        'partner_taxable_investment_accounts': 0.0,
        'partner_other_assets': 0.0,

        # === LIABILITIES (MINIMAL - ONLY 1 VALUE) ===
        'mortgage_balance': 150000.0,
        'primary_residence_mortgage': 150000.0,
        'mortgage_payment': 800.0,
        'mortgage_years': 15,
        'mortgage_rate': 4.0,
        'auto_loans': 0.0,
        'student_loans': 0.0,
        'credit_card_debt': 0.0,
        'personal_loans': 0.0,
        'business_loans': 0.0,
        'other_liabilities': 0.0,
        'secondary_residence_mortgage': 0.0,
        'partner_liabilities': 0.0,

        # === CHILDREN (ONLY 1 CHILD) ===
        'children_list': [
            {
                'Name': 'Child',
                'Birth Year': 2010,
                'College Plan': 'Public In-State',
                'Scholarship %': 0.0,
                'Start Age': 18,
                'Years': 4,
                'Use 529 First?': True
            }
        ],
        'children_rows': [
            {
                'Name': 'Child',
                'Birth Year': 2010,
                'College Plan': 'Public In-State',
                'Scholarship %': 0.0,
                'Start Age': 18,
                'Years': 4,
                'Use 529 First?': True
            }
        ],
        'children_data': [
            {
                'Name': 'Child',
                'Birth Year': 2010,
                'College Plan': 'Public In-State',
                'Scholarship %': 0.0,
                'Start Age': 18,
                'Years': 4,
                'Use 529 First?': True
            }
        ],

        # === INHERITANCES (ONLY 1) ===
        'inheritance_list': [
            {
                'Year': 2030,
                'Amount': 50000.0,
                'Taxable?': False
            }
        ],
        'inherit_rows': [
            {
                'Year': 2030,
                'Amount': 50000.0,
                'Taxable?': False
            }
        ],
        'inheritance_data': [
            {
                'Year': 2030,
                'Amount': 50000.0,
                'Taxable?': False
            }
        ],

        # === GOALS (ONLY 1) ===
        'goals_list': [
            {
                'Goal': 'Retirement Travel',
                'Target $': 30000.0,
                'Target Year': 2028.0,
                'goal': 'Retirement Travel',
                'amount': 30000.0,
                'year': 2028
            }
        ],
        'goals_data': [
            {
                'Goal': 'Retirement Travel',
                'Target $': 30000.0,
                'Target Year': 2028.0,
                'goal': 'Retirement Travel',
                'amount': 30000.0,
                'year': 2028
            }
        ],

        # === SIMULATION PARAMETERS ===
        'simulation_years': 20,
        'tax_rate': 22.0,
        'inflation_rate': 3.0,
        'investment_return_rate': 6.0,
        'mc_iterations': 1000,

        # === COLLEGE COSTS ===
        'college_inflation_input': 4.0,
        'college_inflation_pct': 4.0,
        'public_in_cost_input': 20000.0,
        'public_out_cost_input': 40000.0,
        'private_cost_input': 60000.0,
        'base_public_in': 20000.0,
        'base_public_out': 40000.0,
        'base_private': 60000.0,

        # === LEGACY FIELDS (KEEP FOR COMPATIBILITY) ===
        'subscriptions': 0.0,
        'dining_out': 0.0,
        'entertainment': 0.0,
        'personal_care': 0.0,
        'healthcare': 0.0,
        'transportation': 0.0,
        'clothing': 0.0,
        'food_expenses': 0.0,
        'real_estate_insurance_expenses': 0.0,
        'refresh_scenarios_btn': False,
        'delete_scenario_btn': False,
        'style': 'Detailed Breakdown',
        'children_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'children_data_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'inheritance_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'inheritance_data_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'enhanced_goals_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []}
    },

    # === PRIVATE SCENARIO (TRUSTED USERS ONLY) ===
    '70+_RETIREMENT_SCENARIO_PRIVATE': {
        # Keep minimal private scenario for trusted users
        'user_name': 'Jane Doe',
        'age': 70,
        'partner_exists': False,
        'partner_name': '',
        'partner_age': 0,
        'age_group': '70+',
        'IS_TRUSTED_USER': True,

        'salary_wages': 0.0,
        'social_security_income': 3000.0,
        'pension_income': 2000.0,
        'rental_income': 0.0,
        'self_employment_income': 0.0,
        'investment_income': 0.0,
        'other_income': 0.0,
        'total_income': 5000.0,

        'housing_expenses': 1000.0,
        'utilities_expenses': 200.0,
        'groceries_expenses': 400.0,
        'healthcare_expenses': 500.0,
        'property_tax_expenses': 300.0,
        'transportation_expenses': 0.0,
        'entertainment_expenses': 0.0,
        'restaurant_expenses': 0.0,
        'travel_expenses': 0.0,
        'insurance_expenses': 0.0,
        'education_expenses': 0.0,
        'childcare_expenses': 0.0,
        'clothing_expenses': 0.0,
        'charitable_donations': 0.0,
        'miscellaneous_expenses': 0.0,
        'other_expenses': 0.0,
        'total_expenses': 2400.0,

        'ira_balance': 200000.0,
        'four01k_403b_balance': 150000.0,
        'primary_residence_value': 300000.0,
        'partner_ira_balance': 0,
        'partner_four01k_403b_balance': 0,
        'partner_four01k_balance': 0,
        'taxable_investment_accounts': 0.0,
        'high_yield_savings_account': 0.0,
        'hsa_balance': 0.0,
        'five29_plan_balance': 0.0,
        'secondary_residence_value': 0.0,
        'vehicles_value': 0.0,
        'jewelry_collectibles_value': 0.0,
        'business_ownership_value': 0.0,
        'cryptocurrency_holdings': 0.0,
        'other_assets': 0.0,
        'pension_fund_value': 0.0,

        'mortgage_balance': 0.0,
        'primary_residence_mortgage': 0.0,
        'mortgage_payment': 0.0,
        'mortgage_years': 0,
        'mortgage_rate': 0.0,
        'auto_loans': 0.0,
        'student_loans': 0.0,
        'credit_card_debt': 0.0,
        'personal_loans': 0.0,
        'business_loans': 0.0,
        'other_liabilities': 0.0,
        'secondary_residence_mortgage': 0.0,

        'children_list': [],
        'children_rows': [],
        'children_data': [],
        'inheritance_list': [],
        'inherit_rows': [],
        'inheritance_data': [],
        'goals_list': [],
        'goals_data': [],

        'simulation_years': 15,
        'tax_rate': 20.0,
        'inflation_rate': 3.0,
        'investment_return_rate': 5.0,
        'mc_iterations': 1000,

        'college_inflation_input': 4.0,
        'college_inflation_pct': 4.0,
        'public_in_cost_input': 20000.0,
        'public_out_cost_input': 40000.0,
        'private_cost_input': 60000.0,
        'base_public_in': 20000.0,
        'base_public_out': 40000.0,
        'base_private': 60000.0,

        'children_data_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'inheritance_data_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []},
        'enhanced_goals_editor': {'edited_rows': {}, 'added_rows': [], 'deleted_rows': []}
    }
}
