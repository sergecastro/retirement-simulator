# bulk_document_processor.py - Bulk Folder Processing for Financial Documents
"""
Process entire folders of financial documents at once!

Features:
- Upload entire folder (all PDFs, Word docs, images)
- Auto-organize by document type (bank statements, bills, receipts)
- Smart aggregation across multiple months
- Detect duplicates
- Generate consolidated INTAKE data
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
from statistics import median
import streamlit as st

from document_parser import (
    parse_uploaded_document,
    categorize_transaction,
    calculate_robust_baseline,
    calculate_confidence,
    export_to_intake_format
)


# ============================================================================
# DOCUMENT ORGANIZATION & CLASSIFICATION
# ============================================================================

def classify_document(filename: str, content: Dict) -> str:
    """
    Classify what type of financial document this is.
    Returns: 'bank_statement', 'credit_card', 'bill', 'receipt', 'summary', 'unknown'
    """
    filename_lower = filename.lower()

    # Check filename patterns
    if 'bank' in filename_lower or 'checking' in filename_lower or 'savings' in filename_lower:
        return 'bank_statement'
    elif 'credit' in filename_lower or 'card' in filename_lower:
        return 'credit_card'
    elif any(word in filename_lower for word in ['utility', 'electric', 'gas', 'internet', 'phone']):
        return 'bill'
    elif 'receipt' in filename_lower:
        return 'receipt'
    elif 'summary' in filename_lower or 'budget' in filename_lower:
        return 'summary'

    # Check content patterns
    if 'transactions' in content and len(content.get('transactions', [])) > 5:
        return 'bank_statement'
    elif 'merchant' in content and 'total' in content:
        return 'receipt'
    elif 'income' in content and 'expenses' in content:
        return 'summary'

    return 'unknown'


def extract_date_from_filename(filename: str) -> str:
    """
    Try to extract date from filename.
    Examples:
    - "Bank_Statement_2024-01.pdf" → "2024-01"
    - "Statement_Jan_2024.pdf" → "2024-01"
    """
    # Pattern: YYYY-MM
    match = re.search(r'(\d{4})-(\d{2})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    # Pattern: Mon YYYY
    months = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    for month_name, month_num in months.items():
        if month_name in filename.lower():
            year_match = re.search(r'(\d{4})', filename)
            if year_match:
                return f"{year_match.group(1)}-{month_num}"

    return None


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

def detect_duplicates(documents: List[Dict]) -> List[int]:
    """
    Detect duplicate documents (same content, different filenames).
    Returns list of indices to skip.
    """
    duplicates = []

    for i, doc1 in enumerate(documents):
        if i in duplicates:
            continue

        for j, doc2 in enumerate(documents[i+1:], start=i+1):
            if j in duplicates:
                continue

            # Check if same account and period
            if (doc1.get('account') == doc2.get('account') and
                doc1.get('period_start') == doc2.get('period_start') and
                doc1.get('period_end') == doc2.get('period_end')):

                # Check if transaction counts match (likely duplicate)
                if doc1.get('total_transactions') == doc2.get('total_transactions'):
                    duplicates.append(j)
                    st.info(f"🔍 Duplicate detected: Skipping {doc2.get('_filename', 'unknown')}")

    return duplicates


# ============================================================================
# BULK AGGREGATION
# ============================================================================

def aggregate_transactions_by_category(documents: List[Dict]) -> Dict:
    """
    Aggregate all transactions across multiple documents by category.
    Returns baseline amounts with confidence scores.
    """
    # Collect all transactions by category
    by_category = defaultdict(list)

    for doc in documents:
        if 'transactions' not in doc:
            continue

        for trans in doc['transactions']:
            category = trans.get('category', 'miscellaneous')
            amount = abs(trans.get('amount', 0))  # Use absolute value for expenses

            # Skip refunds from baseline calculation
            if not trans.get('is_refund', False):
                by_category[category].append(amount)

    # Calculate baselines
    aggregated = {}

    for category, amounts in by_category.items():
        if not amounts:
            continue

        # Calculate robust baseline (median preferred)
        baseline, confidence = calculate_robust_baseline(amounts, method="median")

        aggregated[category] = {
            'monthly_baseline': round(baseline, 2),
            'confidence': confidence,
            'data_points': len(amounts),
            'min': min(amounts),
            'max': max(amounts),
            'median': median(amounts)
        }

    return aggregated


def aggregate_income_sources(documents: List[Dict]) -> Dict:
    """
    Aggregate income across documents.
    """
    income_by_type = defaultdict(list)

    for doc in documents:
        if 'income' not in doc:
            continue

        for income_type, amount in doc['income'].items():
            income_by_type[income_type].append(amount)

    # Calculate baselines
    aggregated = {}

    for income_type, amounts in income_by_type.items():
        if not amounts:
            continue

        baseline, confidence = calculate_robust_baseline(amounts, method="median")

        aggregated[income_type] = {
            'monthly_baseline': round(baseline, 2),
            'confidence': confidence,
            'data_points': len(amounts)
        }

    return aggregated


# ============================================================================
# MAIN BULK PROCESSING FUNCTION
# ============================================================================

def process_bulk_documents(uploaded_files: List) -> Dict:
    """
    Process multiple documents at once.

    Returns:
    {
        'documents_processed': int,
        'documents_by_type': Dict,
        'aggregated_expenses': Dict,
        'aggregated_income': Dict,
        'date_range': (start, end),
        'intake_format': Dict,
        'warnings': List[str]
    }
    """
    if not uploaded_files:
        return {'error': 'No files uploaded'}

    st.info(f"📂 Processing {len(uploaded_files)} documents...")

    # Parse all documents
    parsed_docs = []
    warnings = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Parsing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        progress_bar.progress((i + 1) / len(uploaded_files))

        try:
            parsed = parse_uploaded_document(uploaded_file)

            if 'error' in parsed:
                warnings.append(f"⚠️ {uploaded_file.name}: {parsed['error']}")
            else:
                parsed['_filename'] = uploaded_file.name
                parsed['_doc_type'] = classify_document(uploaded_file.name, parsed)
                parsed['_date_hint'] = extract_date_from_filename(uploaded_file.name)
                parsed_docs.append(parsed)

        except Exception as e:
            warnings.append(f"❌ {uploaded_file.name}: {str(e)}")

    progress_bar.empty()
    status_text.empty()

    if not parsed_docs:
        return {'error': 'No documents could be parsed', 'warnings': warnings}

    # Detect and skip duplicates
    duplicates = detect_duplicates(parsed_docs)
    parsed_docs = [doc for i, doc in enumerate(parsed_docs) if i not in duplicates]

    st.success(f"✅ Successfully parsed {len(parsed_docs)} unique documents")

    # Organize by type
    by_type = defaultdict(list)
    for doc in parsed_docs:
        doc_type = doc.get('_doc_type', 'unknown')
        by_type[doc_type].append(doc)

    # Aggregate data
    aggregated_expenses = aggregate_transactions_by_category(parsed_docs)
    aggregated_income = aggregate_income_sources(parsed_docs)

    # Determine date range
    dates = []
    for doc in parsed_docs:
        if doc.get('_date_hint'):
            dates.append(doc['_date_hint'])

    date_range = (min(dates), max(dates)) if dates else (None, None)

    # Convert to INTAKE format
    intake_data = {}

    # Map aggregated expenses to INTAKE fields
    expense_field_map = {
        'housing': 'input_housing_expenses',
        'utilities': 'input_utilities_expenses',
        'groceries': 'input_groceries_expenses',
        'dining': 'input_restaurant_expenses',
        'transportation': 'input_transportation_expenses',
        'healthcare': 'input_healthcare_expenses',
        'insurance': 'input_insurance_expenses',
        'entertainment': 'input_entertainment_expenses',
        'travel': 'input_travel_expenses',
        'education': 'input_education_expenses',
        'miscellaneous': 'input_miscellaneous_expenses'
    }

    for category, data in aggregated_expenses.items():
        field_name = expense_field_map.get(category, 'input_other_expenses')
        intake_data[field_name] = data['monthly_baseline']

    # Map aggregated income to INTAKE fields
    for income_type, data in aggregated_income.items():
        if 'salary' in income_type.lower() or 'wage' in income_type.lower():
            intake_data['input_salary_wages'] = data['monthly_baseline']
        elif 'social security' in income_type.lower():
            intake_data['input_social_security_income'] = data['monthly_baseline']
        elif 'pension' in income_type.lower():
            intake_data['input_pension_income'] = data['monthly_baseline']

    # Calculate totals
    total_expenses = sum(data['monthly_baseline'] for data in aggregated_expenses.values())
    total_income = sum(data['monthly_baseline'] for data in aggregated_income.values())

    intake_data['input_total_expenses'] = round(total_expenses, 2)
    intake_data['input_total_income'] = round(total_income, 2)

    # Add confidence metadata
    intake_data['_confidence_by_category'] = {
        category: data['confidence']
        for category, data in aggregated_expenses.items()
    }

    return {
        'documents_processed': len(parsed_docs),
        'documents_skipped': len(duplicates),
        'documents_by_type': {doc_type: len(docs) for doc_type, docs in by_type.items()},
        'aggregated_expenses': aggregated_expenses,
        'aggregated_income': aggregated_income,
        'date_range': date_range,
        'intake_format': intake_data,
        'warnings': warnings,
        'raw_documents': parsed_docs  # For detailed inspection
    }


# ============================================================================
# VISUALIZATION HELPERS
# ============================================================================

def show_aggregation_summary(result: Dict):
    """Display a nice summary of the aggregation results"""

    st.header("📊 Aggregation Summary")

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Documents Processed", result['documents_processed'])
    with col2:
        if result.get('documents_skipped', 0) > 0:
            st.metric("Duplicates Skipped", result['documents_skipped'])
        else:
            st.metric("Duplicates", "None ✅")
    with col3:
        date_range = result.get('date_range', (None, None))
        if date_range[0] and date_range[1]:
            st.metric("Date Range", f"{date_range[0]} to {date_range[1]}")
        else:
            st.metric("Date Range", "Unknown")
    with col4:
        total_expense = result['intake_format'].get('input_total_expenses', 0)
        st.metric("Monthly Expenses", f"${total_expense:,.2f}")

    # Document types breakdown
    st.subheader("📁 By Document Type")
    for doc_type, count in result['documents_by_type'].items():
        st.write(f"**{doc_type.replace('_', ' ').title()}:** {count} documents")

    st.divider()

    # AUDIT RECONCILIATION
    st.subheader("🔍 Audit Reconciliation")

    # Calculate totals across ALL documents
    categorized_total = 0
    skipped_total = 0
    total_categorized_count = 0
    total_skipped_count = 0

    all_skipped_transactions = []

    for doc in result.get('raw_documents', []):
        # Categorized transactions
        for trans in doc.get('transactions', []):
            categorized_total += abs(trans.get('amount', 0))
            total_categorized_count += 1

        # Skipped transactions
        for trans in doc.get('skipped_transactions', []):
            skipped_total += abs(trans.get('amount', 0))
            total_skipped_count += 1

            # Add to all_skipped with source file info
            all_skipped_transactions.append({
                'Date': trans.get('date', 'N/A'),
                'Description': trans.get('description', 'N/A')[:60],
                'Amount': abs(trans.get('amount', 0)),
                'Reason': trans.get('skip_reason', 'Unknown'),
                'From': doc.get('_filename', 'Unknown')[:30]
            })

    grand_total = categorized_total + skipped_total

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Categorized Total", f"${categorized_total:,.2f}",
                help=f"{total_categorized_count} transactions included")
    with col2:
        st.metric("Skipped Total", f"${skipped_total:,.2f}",
                help=f"{total_skipped_count} transactions excluded")
    with col3:
        st.metric("Grand Total", f"${grand_total:,.2f}",
                help="Sum of categorized + skipped (should match all statement totals)")

    # Show all skipped transactions table
    if all_skipped_transactions:
        with st.expander(f"⚠️ View All Skipped/Uncategorized Transactions ({total_skipped_count})"):
            st.caption("These transactions were excluded from categorization:")
            import pandas as pd
            skipped_df = pd.DataFrame(all_skipped_transactions)
            st.dataframe(skipped_df, use_container_width=True,
                        height=min(400, len(all_skipped_transactions) * 35 + 38))

            st.caption(f"**Skipped Total:** ${skipped_total:,.2f}")
    else:
        st.info("✅ No transactions were skipped - all transactions were categorized")

    st.divider()

    # Expense breakdown
    st.subheader("💰 Monthly Expense Baseline (By Category)")

    expenses = result['aggregated_expenses']
    if expenses:
        # Sort by amount
        sorted_expenses = sorted(expenses.items(), key=lambda x: x[1]['monthly_baseline'], reverse=True)

        for category, data in sorted_expenses:
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                # Color code by confidence
                confidence = data['confidence']
                if confidence >= 0.90:
                    st.success(f"**{category.title()}**")
                elif confidence >= 0.75:
                    st.info(f"**{category.title()}**")
                else:
                    st.warning(f"**{category.title()}**")

            with col2:
                st.write(f"${data['monthly_baseline']:,.2f}/month")

            with col3:
                st.write(f"📊 {data['data_points']} data points | Confidence: {confidence:.0%}")

            # Add expandable details showing individual transactions
            with st.expander(f"🔍 View {category.title()} Details"):
                st.caption(f"Individual transactions in this category:")

                # Get all transactions for this category from raw documents
                category_transactions = []
                for doc in result.get('raw_documents', []):
                    if 'transactions' not in doc:
                        continue
                    for trans in doc['transactions']:
                        if trans.get('category') == category:
                            category_transactions.append({
                                'Date': trans.get('date', 'N/A'),
                                'Description': trans.get('description', 'N/A')[:50],  # Truncate long descriptions
                                'Amount': abs(trans.get('amount', 0)),
                                'From': doc.get('_filename', 'Unknown')[:30]
                            })

                if category_transactions:
                    import pandas as pd
                    df = pd.DataFrame(category_transactions)
                    st.dataframe(df, use_container_width=True, height=min(300, len(category_transactions) * 35 + 38))

                    # Show statistics
                    amounts = [t['Amount'] for t in category_transactions]
                    st.write(f"**Min:** ${min(amounts):,.2f} | **Max:** ${max(amounts):,.2f} | **Median:** ${data['median']:,.2f}")
                else:
                    st.write("No detailed transactions available")
    else:
        st.info("No expense data found")

    st.divider()

    # Income breakdown
    if result['aggregated_income']:
        st.subheader("💵 Monthly Income Sources")

        for income_type, data in result['aggregated_income'].items():
            col1, col2 = st.columns([3, 2])

            with col1:
                st.write(f"**{income_type.title()}**")
            with col2:
                st.write(f"${data['monthly_baseline']:,.2f}/month | {data['data_points']} data points")

    # Warnings
    if result.get('warnings'):
        st.divider()
        st.subheader("⚠️ Warnings")
        for warning in result['warnings']:
            st.warning(warning)
