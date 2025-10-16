# test_document_parser.py - Standalone Test App for Document Parser
"""
SAFE TEST APP - Does not modify any existing code!

Run this app to test document parsing before integrating into INTAKE:
    streamlit run test_document_parser.py --server.port 8504

Tests:
- PDF upload and parsing
- Word document parsing
- Image OCR (if available)
- Shows extracted data before applying to intake
"""

import streamlit as st
import json

# Try to import document parser
try:
    from document_parser import (
        parse_uploaded_document,
        export_to_intake_format,
        PDF_AVAILABLE,
        DOCX_AVAILABLE,
        OCR_AVAILABLE
    )
    PARSER_AVAILABLE = True
except ImportError as e:
    PARSER_AVAILABLE = False
    import_error = str(e)

st.set_page_config(
    page_title="Document Parser Test",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document Parser Test App")
st.caption("Safe testing environment - does not modify your INTAKE or main app!")

# Show library status
st.header("🔍 Library Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if PARSER_AVAILABLE:
        st.success("✅ Parser Module")
    else:
        st.error("❌ Parser Module")
        st.error(f"Error: {import_error}")

with col2:
    if PARSER_AVAILABLE and PDF_AVAILABLE:
        st.success("✅ PDF Support")
    else:
        st.warning("⚠️ PDF Support")
        st.caption("pip install PyPDF2")

with col3:
    if PARSER_AVAILABLE and DOCX_AVAILABLE:
        st.success("✅ Word Support")
    else:
        st.warning("⚠️ Word Support")
        st.caption("pip install python-docx")

with col4:
    if PARSER_AVAILABLE and OCR_AVAILABLE:
        st.success("✅ OCR Support")
    else:
        st.info("ℹ️ OCR Optional")
        st.caption("pip install pytesseract pillow")

if not PARSER_AVAILABLE:
    st.error("❌ Cannot proceed - document_parser.py not found or has import errors")
    st.stop()

# Installation instructions
if not (PDF_AVAILABLE and DOCX_AVAILABLE):
    with st.expander("📦 Installation Instructions"):
        st.code("""
# Install Phase 2 dependencies:
pip install -r requirements_phase2.txt

# Or install individually:
pip install PyPDF2>=3.0.0
pip install python-docx>=1.0.0
pip install pytesseract>=0.3.10 pillow>=10.0.0  # Optional, for OCR
        """)

st.divider()

# File upload section
st.header("📤 Upload Documents")

# Choose upload mode
upload_mode = st.radio(
    "Upload Mode:",
    ["Single Document", "Multiple Documents (Bulk)"],
    help="Single: Test one file | Bulk: Upload entire folder of statements"
)

if upload_mode == "Single Document":
    st.info("Upload a bank statement, bill, financial summary, or receipt to test parsing")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'bmp'],
        help="Supported: PDF, Word documents, and images (with OCR)"
    )
    uploaded_files = [uploaded_file] if uploaded_file else []

else:  # Multiple documents
    st.info("🚀 **FAST MODE:** Upload an entire folder of financial documents at once!")
    st.caption("The system will automatically organize, deduplicate, and aggregate across all files")

    uploaded_files = st.file_uploader(
        "Choose multiple files",
        type=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'bmp'],
        accept_multiple_files=True,
        help="Select all files in your folder (Ctrl+A or Cmd+A)"
    )

if uploaded_files:
    if upload_mode == "Single Document":
        st.success(f"✅ Uploaded: {uploaded_files[0].name} ({uploaded_files[0].type})")

        # Show file details
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Name", uploaded_files[0].name)
        with col2:
            st.metric("File Size", f"{uploaded_files[0].size / 1024:.1f} KB")

        parse_button_label = "🔍 Parse Document"
    else:
        st.success(f"✅ Uploaded {len(uploaded_files)} documents")

        # Show total size
        total_size = sum(f.size for f in uploaded_files) / 1024 / 1024  # MB
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Files", len(uploaded_files))
        with col2:
            st.metric("Total Size", f"{total_size:.2f} MB")

        # Show file list
        with st.expander("📋 View File List"):
            for i, f in enumerate(uploaded_files, 1):
                st.write(f"{i}. {f.name} ({f.size / 1024:.1f} KB)")

        parse_button_label = "🚀 Process All Documents"

    st.divider()

    # Debug mode toggle
    debug_mode = st.checkbox("🔍 Enable Debug Mode (show raw extracted text)", value=False)

    # Parse button
    if st.button(parse_button_label, type="primary", use_container_width=True):
        # Handle bulk or single mode
        if upload_mode == "Multiple Documents (Bulk)":
            # Import bulk processor
            try:
                from bulk_document_processor import process_bulk_documents, show_aggregation_summary

                with st.spinner(f"Processing {len(uploaded_files)} documents..."):
                    result = process_bulk_documents(uploaded_files)

                    if 'error' in result:
                        st.error(f"❌ Error: {result['error']}")
                        if result.get('warnings'):
                            for warning in result['warnings']:
                                st.warning(warning)
                    else:
                        st.success(f"✅ Processed {result['documents_processed']} documents!")

                        # Show aggregation summary
                        show_aggregation_summary(result)

                        st.divider()

                        # Download INTAKE format
                        st.subheader("📥 Export to INTAKE")
                        intake_data = result['intake_format']

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Monthly Expenses", f"${intake_data.get('input_total_expenses', 0):,.2f}")
                        with col2:
                            st.metric("Total Monthly Income", f"${intake_data.get('input_total_income', 0):,.2f}")

                        # Download button
                        json_str = json.dumps(intake_data, indent=2)
                        st.download_button(
                            label="📥 Download for INTAKE App",
                            data=json_str,
                            file_name="bulk_parsed_intake_data.json",
                            mime="application/json",
                            use_container_width=True
                        )

                        st.success("💡 **Next:** Load this JSON file into your INTAKE app using 'Load from path'")

            except ImportError as e:
                st.error(f"❌ Bulk processor not available: {e}")

        else:
            # Single document mode
            with st.spinner("Parsing document..."):
                try:
                    # Parse the document
                    parsed_data = parse_uploaded_document(uploaded_files[0], debug=debug_mode)

                    if "error" in parsed_data:
                        st.error(f"❌ Error: {parsed_data['error']}")
                    else:
                        st.success("✅ Document parsed successfully!")

                    # Initialize session state for transaction edits if not exists
                    if 'edited_transactions' not in st.session_state:
                        st.session_state['edited_transactions'] = None

                    # Show results in tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "✏️ Review & Edit", "🔧 Raw Data", "📥 INTAKE Format"])

                    with tab1:
                        st.subheader("Extracted Data Summary")

                        # Bank statement specifics
                        if "account" in parsed_data:
                            st.write(f"**Account:** {parsed_data['account']}")
                            if parsed_data.get('period_start') and parsed_data.get('period_end'):
                                st.write(f"**Period:** {parsed_data['period_start']} to {parsed_data['period_end']}")

                        # AUDIT RECONCILIATION
                        st.divider()
                        st.subheader("🔍 Audit Reconciliation")

                        categorized_total = sum(abs(t['amount']) for t in parsed_data.get('transactions', []))
                        skipped_total = sum(abs(t['amount']) for t in parsed_data.get('skipped_transactions', []))
                        grand_total = categorized_total + skipped_total

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Categorized Total", f"${categorized_total:,.2f}",
                                    help=f"{parsed_data.get('total_transactions', 0)} transactions")
                        with col2:
                            st.metric("Skipped Total", f"${skipped_total:,.2f}",
                                    help=f"{parsed_data.get('total_skipped', 0)} transactions")
                        with col3:
                            st.metric("Grand Total", f"${grand_total:,.2f}",
                                    help="Sum of categorized + skipped")

                        # Show skipped transactions
                        if parsed_data.get('skipped_transactions'):
                            st.divider()
                            st.subheader("⚠️ Skipped/Uncategorized Transactions")
                            st.caption(f"{len(parsed_data['skipped_transactions'])} transactions were skipped (not included in INTAKE)")

                            import pandas as pd
                            skipped_df = pd.DataFrame(parsed_data['skipped_transactions'])
                            st.dataframe(skipped_df, use_container_width=True, height=min(300, len(parsed_data['skipped_transactions']) * 35 + 38))

                        st.divider()

                        # Transactions
                        if "transactions" in parsed_data:
                            st.write(f"**Total Transactions:** {parsed_data['total_transactions']}")

                            # Group by category
                            from collections import defaultdict
                            by_category = defaultdict(list)

                            for trans in parsed_data["transactions"]:
                                category = trans.get("category", "unknown")
                                amount = trans.get("amount", 0)
                                by_category[category].append(amount)

                            # Show category totals with expandable details
                            st.subheader("💰 By Category")
                            for category, amounts in sorted(by_category.items()):
                                total = sum(amounts)
                                avg = total / len(amounts) if amounts else 0

                                # Category summary
                                st.write(f"**{category.title()}:** ${total:,.2f} total | ${avg:,.2f} avg | {len(amounts)} transactions")

                                # Expandable detail for this category
                                with st.expander(f"🔍 View {category.title()} Details"):
                                    # Get all transactions for this category
                                    category_transactions = [
                                        t for t in parsed_data["transactions"]
                                        if t.get("category") == category
                                    ]

                                    if category_transactions:
                                        import pandas as pd
                                        # Create DataFrame with relevant columns
                                        df = pd.DataFrame(category_transactions)[['date', 'description', 'amount']]
                                        st.dataframe(df, use_container_width=True, height=min(400, len(category_transactions) * 35 + 38))
                                    else:
                                        st.write("No transactions in this category")

                            # Show ALL transactions
                            with st.expander("📋 View All Transactions"):
                                import pandas as pd
                                df = pd.DataFrame(parsed_data["transactions"])
                                st.dataframe(df, use_container_width=True)

                        # Word document specifics
                        if "income" in parsed_data and "expenses" in parsed_data:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("💰 Income Found")
                                if parsed_data["income"]:
                                    for label, amount in parsed_data["income"].items():
                                        st.write(f"**{label.title()}:** ${amount:,.2f}")
                                else:
                                    st.write("No income detected")

                            with col2:
                                st.subheader("🏠 Expenses Found")
                                if parsed_data["expenses"]:
                                    for category, amount in parsed_data["expenses"].items():
                                        st.write(f"**{category.title()}:** ${amount:,.2f}")
                                else:
                                    st.write("No expenses detected")

                        # Receipt specifics
                        if "merchant" in parsed_data:
                            st.write(f"**Merchant:** {parsed_data['merchant']}")
                            st.write(f"**Total:** ${parsed_data['total']:,.2f}")
                            st.write(f"**Category:** {parsed_data['category']}")

                    with tab2:
                        st.subheader("✏️ Review & Edit Transactions")
                        st.caption("Remove unwanted transactions or change their categories before exporting to INTAKE")

                        if "transactions" in parsed_data and parsed_data["transactions"]:
                            import pandas as pd

                            # Use edited transactions if available, otherwise use parsed data
                            if st.session_state['edited_transactions'] is None:
                                current_transactions = parsed_data["transactions"].copy()
                            else:
                                current_transactions = st.session_state['edited_transactions']

                            # Available categories
                            categories = ["housing", "utilities", "groceries", "dining", "transportation",
                                        "healthcare", "insurance", "entertainment", "travel", "education", "miscellaneous"]

                            st.write(f"**Total Transactions:** {len(current_transactions)}")

                            # Create editable table
                            edited_transactions = []
                            transactions_to_remove = []

                            for idx, trans in enumerate(current_transactions):
                                col1, col2, col3, col4, col5 = st.columns([1, 2, 4, 2, 1.5])

                                with col1:
                                    # Checkbox to remove
                                    remove = st.checkbox("❌", key=f"remove_{idx}", help="Check to remove this transaction")
                                    if remove:
                                        transactions_to_remove.append(idx)

                                with col2:
                                    st.text(trans['date'])

                                with col3:
                                    # Truncate long descriptions
                                    desc = trans['description']
                                    if len(desc) > 60:
                                        desc = desc[:60] + "..."
                                    st.text(desc)

                                with col4:
                                    st.text(f"${abs(trans['amount']):,.2f}")

                                with col5:
                                    # Dropdown to change category
                                    current_cat = trans.get('category', 'miscellaneous')
                                    new_cat = st.selectbox(
                                        "Category",
                                        options=categories,
                                        index=categories.index(current_cat) if current_cat in categories else 0,
                                        key=f"cat_{idx}",
                                        label_visibility="collapsed"
                                    )
                                    trans['category'] = new_cat

                                if not remove:
                                    edited_transactions.append(trans)

                            # Show summary of changes
                            if transactions_to_remove:
                                st.warning(f"⚠️ {len(transactions_to_remove)} transaction(s) will be removed")

                            # Apply changes button
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("💾 Apply Changes", type="primary", use_container_width=True):
                                    st.session_state['edited_transactions'] = edited_transactions
                                    st.success(f"✅ Changes applied! {len(edited_transactions)} transactions remaining.")
                                    st.rerun()

                            with col2:
                                if st.button("🔄 Reset to Original", use_container_width=True):
                                    st.session_state['edited_transactions'] = None
                                    st.success("✅ Reset to original parsed data")
                                    st.rerun()

                            # Update parsed_data with edited transactions for export
                            parsed_data["transactions"] = edited_transactions
                            parsed_data["total_transactions"] = len(edited_transactions)

                        else:
                            st.info("No transactions to edit")

                    with tab3:
                        st.subheader("Raw Parsed Data")
                        st.json(parsed_data, expanded=False)

                    with tab4:
                        st.subheader("INTAKE App Format Preview")
                        st.caption("This shows how the data would be formatted for your INTAKE app")

                        try:
                            intake_format = export_to_intake_format(parsed_data, smoothing="exact")

                            if intake_format:
                                st.json(intake_format, expanded=True)

                                st.divider()
                                st.info("💡 **Next Step:** Once you're confident this works, we can add this to your INTAKE app!")

                                # Download button
                                json_str = json.dumps(intake_format, indent=2)
                                st.download_button(
                                    label="📥 Download as JSON",
                                    data=json_str,
                                    file_name="parsed_intake_data.json",
                                    mime="application/json"
                                )
                            else:
                                st.warning("⚠️ Could not convert to INTAKE format")

                        except Exception as e:
                            st.error(f"Error converting to INTAKE format: {e}")

                except Exception as e:
                    st.error(f"❌ Parsing failed: {str(e)}")
                    st.exception(e)

else:
    st.info("👆 Upload a document above to start testing")

# Tips section
st.divider()
with st.expander("💡 Testing Tips"):
    st.markdown("""
    ### Good Test Documents:
    - **Bank statement PDF** - Best for testing transaction extraction
    - **Credit card statement PDF** - Tests categorization
    - **Word document** - Type some expenses manually to test
    - **Receipt photo** - Tests OCR (requires pytesseract installed)

    ### What to Look For:
    1. ✅ Are transactions extracted correctly?
    2. ✅ Is categorization accurate? (groceries, dining, utilities)
    3. ✅ Are transfers skipped? (Venmo, Zelle, etc.)
    4. ✅ Does the INTAKE format look correct?

    ### If Something Goes Wrong:
    - Check the "Raw Data" tab to see what was extracted
    - Try a different document format
    - Check that libraries are installed (see status above)

    ### When Ready:
    Once this works reliably, we'll add it as an optional feature in your INTAKE app!
    """)

# Footer
st.divider()
st.caption("📄 Document Parser Test App v1.0 | Safe testing environment")
st.caption("Changes made here do NOT affect your main INTAKE or simulator apps")
