# document_parser.py - Intelligent PDF/Word/Image Document Parser
"""
Phase 2: Document Reading System for Retirement INTAKE
Implements GROK's sophisticated analysis rules for financial statement parsing.

Features:
- PDF text extraction (PyPDF2)
- Word document parsing (python-docx)
- Image OCR (pytesseract, easyocr as fallback)
- Smart month normalization with proration
- Robust baseline calculation (median, EMWA, seasonal)
- Category-specific logic
- Confidence scoring
- Double-counting prevention
"""

import re
import io
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from statistics import median
import streamlit as st

# Document parsing libraries (with graceful fallback if not installed)
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    st.warning("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed. Install with: pip install python-docx")

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # OCR is optional, no warning needed yet


# ============================================================================
# CATEGORY MAPPING & DETECTION
# ============================================================================

EXPENSE_CATEGORIES = {
    "housing": ["mortgage", "rent", "hoa", "property management", "homeowners association", "maintenance assoc", "maint assoc",
                "tax collector", "property tax", "oak creek", "positano", "paseo westpark", "foothill ranch", "kenwood com"],
    "utilities": ["electric", "gas", "water", "internet", "cable", "phone", "cell", "verizon", "at&t", "comcast", "pool service",
                  "edison", "southern california edison", "sce", "southern california gas", "irvine ranch water", "waste management"],
    "groceries": ["grocery", "safeway", "kroger", "walmart", "whole foods", "trader joe", "costco", "sam's club"],
    "dining": ["restaurant", "dining", "uber eats", "doordash", "grubhub", "starbucks", "mcdonald", "chipotle"],
    "transportation": ["gas", "fuel", "chevron", "shell", "exxon", "car payment", "auto loan", "auto finance", "mercury ins", "dmv",
                       "subaru motors finance", "chase auto finance"],
    "healthcare": ["medical", "doctor", "hospital", "pharmacy", "cvs", "walgreens", "prescription", "dental"],
    "insurance": ["insurance premium", "life insurance", "health insurance", "homeowner insurance", "renters insurance", "geico", "state farm", "progressive", "allstate"],
    "entertainment": ["netflix", "hulu", "disney", "spotify", "apple music", "gym", "fitness", "movie", "theater"],
    "travel": ["airline", "hotel", "airbnb", "vrbo", "expedia", "booking", "flight"],
    "education": ["tuition", "school", "university", "college", "student loan"],
    "miscellaneous": []  # catch-all
}

INCOME_KEYWORDS = [
    "salary", "paycheck", "direct deposit", "wages", "pension", "social security",
    "ssa", "retirement", "dividend", "interest", "rental income", "bonus"
]

TRANSFER_KEYWORDS = [
    "transfer", "zelle", "venmo", "paypal", "cash app", "payment from", "payment to",
    "ach transfer", "wire transfer", "internal transfer"
]

# Credit card payments = double-counting (expense already captured on card statement)
# IMPORTANT: Must be very specific to avoid false positives!
CREDIT_CARD_PAYMENT_KEYWORDS = [
    "credit card bill payment", "credit cards bill payment",
    "chase credit card", "citibank credit card", "tjx rewards credit card",
    "amex", "discover card", "capital one", "barclays", "synchrony"
]

# Non-transaction indicators (skip these)
NON_TRANSACTION_KEYWORDS = [
    "days in billing", "billing cycle", "statement period", "account summary",
    "previous balance", "new balance", "total credits", "total debits",
    "enter payment", "page ", "continued", "subtotal", "counter credit",
    # ATM withdrawals and deposits (not expenses - just cash movement)
    "atm", "deposit", "withdrwl", "withdrawal", "cash withdrawal",
    # Interest earned is income but too small to matter in retirement planning
    "interest earned"
]

REFUND_KEYWORDS = ["refund", "return", "credit", "reversal", "chargeback"]


def categorize_transaction(description: str, amount: float) -> Tuple[str, bool, bool]:
    """
    Categorize a transaction by description.
    Returns: (category, is_transfer_or_skip, is_refund)

    is_transfer_or_skip = True means skip this line (transfers, payments, non-transactions)
    """
    desc_lower = description.lower()

    # 1. Check if it's a non-transaction line (skip)
    for keyword in NON_TRANSACTION_KEYWORDS:
        if keyword in desc_lower:
            return ("non_transaction", True, False)

    # 2. Check if it's a credit card payment (skip to avoid double-counting)
    for keyword in CREDIT_CARD_PAYMENT_KEYWORDS:
        if keyword in desc_lower:
            return ("credit_card_payment", True, False)

    # 3. Check if it's a transfer (skip these)
    for keyword in TRANSFER_KEYWORDS:
        if keyword in desc_lower:
            return ("transfer", True, False)

    # 4. Check if description looks like a check number only (e.g., "579", "580")
    # These are unclear without more context - skip them
    if desc_lower.strip().isdigit() and len(desc_lower.strip()) <= 5:
        return ("check_number_only", True, False)

    # 5. Check if it's a refund (special handling)
    for keyword in REFUND_KEYWORDS:
        if keyword in desc_lower:
            # Try to match original category
            for category, keywords in EXPENSE_CATEGORIES.items():
                for kw in keywords:
                    if kw in desc_lower:
                        return (category, False, True)
            return ("miscellaneous", False, True)

    # 6. Check if it's income (positive amount usually)
    if amount > 0:
        for keyword in INCOME_KEYWORDS:
            if keyword in desc_lower:
                return ("income", False, False)

    # 7. Categorize expense
    for category, keywords in EXPENSE_CATEGORIES.items():
        for kw in keywords:
            if kw in desc_lower:
                return (category, False, False)

    return ("miscellaneous", False, False)


# ============================================================================
# PDF PARSING
# ============================================================================

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {e}")
        return ""


def parse_bank_statement_pdf(pdf_file, debug=False) -> Dict:
    """
    Parse a bank statement PDF and extract transactions.
    Returns structured data with amounts, dates, descriptions.
    """
    text = extract_text_from_pdf(pdf_file)

    if not text:
        return {"error": "Could not extract text from PDF"}

    # DEBUG: Show extracted text
    if debug:
        st.text_area("🔍 DEBUG: Extracted PDF Text (first 3000 chars)", text[:3000], height=400)

    # Extract account info
    account_match = re.search(r"Account\s+(?:Number|#)?:?\s*([\d\-]+)", text, re.IGNORECASE)
    account_number = account_match.group(1) if account_match else "Unknown"

    # Extract statement period
    period_match = re.search(r"Statement\s+Period:?\s*(\d{1,2}/\d{1,2}/\d{2,4})\s*-\s*(\d{1,2}/\d{1,2}/\d{2,4})", text, re.IGNORECASE)
    start_date = period_match.group(1) if period_match else None
    end_date = period_match.group(2) if period_match else None

    # Extract transactions - Bank of America specific format
    # Look for "Other subtractions" section (real expenses, not ATM withdrawals)
    # Format: Date on one line, Description (may wrap multiple lines), Amount on last line

    transactions = []

    # NEW APPROACH: Find "Date Description Amount" header, then parse everything after it
    # Split entire document into lines
    all_lines = text.split('\n')

    # Find all "Date Description Amount" headers
    header_indices = []
    for idx, line in enumerate(all_lines):
        # Look for the exact pattern "Date" followed by "Description" followed by "Amount"
        if re.search(r'Date\s+Description\s+Amount', line, re.IGNORECASE):
            header_indices.append(idx)

    if debug:
        st.write(f"🔍 Found {len(header_indices)} 'Date Description Amount' headers at line numbers: {header_indices}")

    transactions_found = 0

    # Process each section after a "Date Description Amount" header
    for header_idx in header_indices:
        if debug:
            st.write(f"\n📝 Processing section starting at line {header_idx}")
            st.write("Next 10 lines after header:")
            for offset in range(1, min(11, len(all_lines) - header_idx)):
                st.text(f"  {header_idx + offset}: '{all_lines[header_idx + offset]}'")

        # Start reading from line after the header
        i = header_idx + 1

        while i < len(all_lines):
            line = all_lines[i].strip()

            # Stop if we hit a section total or next header
            if re.search(r'Total|continued on|Checks', line, re.IGNORECASE):
                break

            # RULE: Every transaction MUST start with a date
            # Format: MM/DD/YY or MM/DD/YYYY
            date_match = re.match(r'^(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+)', line)

            if not date_match:
                # No date = not a transaction line, skip it
                i += 1
                continue

            # We found a date! Extract it
            date_str = date_match.group(1)
            rest_of_line = date_match.group(2).strip()

            # RULE: Transaction MUST have an amount (negative number with .XX)
            # Check if amount is on the same line (may have trailing spaces)
            amount_match = re.search(r'(-[\d,]+\.\d{2})\s*$', rest_of_line)

            if amount_match:
                # CASE 1: Date, Description, Amount all on same line
                # Example: 12/02/19 SOUTHERN CALIFORNIA EDISON SCE Bill Payment -342.37
                amount_str = amount_match.group(1).replace(",", "")
                description = rest_of_line[:amount_match.start()].strip()
                i += 1
            else:
                # CASE 2: Amount on next line(s)
                # Example:
                # 12/03/19 VANGUARD DES:EDI PYMNTS ID:000000004854965 INDN:SERGE CASTRO CO
                # ID:9231945930 PPD
                # -0.99

                description_parts = [rest_of_line]
                amount_str = None

                # Look ahead maximum 3 lines for the amount
                for lookahead in range(1, 4):
                    if i + lookahead >= len(all_lines):
                        break

                    next_line = all_lines[i + lookahead].strip()

                    # Stop if we hit another date (means this transaction has no amount)
                    if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}\s', next_line):
                        break

                    # Check if this line is ONLY an amount
                    if re.match(r'^-[\d,]+\.\d{2}$', next_line):
                        amount_str = next_line.replace(",", "")
                        i += lookahead + 1
                        break
                    else:
                        # This line is part of description
                        description_parts.append(next_line)

                # If no amount found, skip this "transaction" (it's not a real transaction)
                if amount_str is None:
                    i += 1
                    continue

                description = " ".join(description_parts)

            # Now we have: date_str, description, amount_str
            # Clean up and process
            try:
                amount = float(amount_str)

                # Clean description
                description = " ".join(description.split())
                if len(description) > 100:
                    description = description[:100] + "..."

                category, is_skip, is_refund = categorize_transaction(description, amount)

                # Skip transfers, credit card payments, non-transactions
                if not is_skip:
                    transactions.append({
                        "date": date_str,
                        "description": description,
                        "amount": amount,
                        "category": category,
                        "is_refund": is_refund
                    })
                    transactions_found += 1
            except ValueError:
                # Amount couldn't be parsed as float, skip
                pass

        if debug:
            st.write(f"✅ Found {transactions_found} valid transactions (after filtering)")

    # Also try to find deposits/income in "Deposits and other additions" section
    deposits_match = re.search(r"Deposits and other additions\s+Date\s+Description\s+Amount\s+(.+?)(?:Total deposits|Withdrawals|$)", text, re.DOTALL | re.IGNORECASE)

    if deposits_match:
        section_text = deposits_match.group(1)

        # Pattern for positive amounts (deposits/income)
        income_pattern = r"(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+([\d,]+\.\d{2})"

        for match in re.finditer(income_pattern, section_text, re.DOTALL):
            date_str = match.group(1)
            description_raw = match.group(2)
            amount_str = match.group(3).replace(",", "")

            description = " ".join(description_raw.split())
            if len(description) > 100:
                description = description[:100] + "..."

            try:
                amount = float(amount_str)

                # Only capture income (SSA, pension, etc), skip ATM deposits and counter credits
                if "ssa treas" in description.lower() or "social security" in description.lower():
                    transactions.append({
                        "date": date_str,
                        "description": description,
                        "amount": amount,
                        "category": "income",
                        "is_refund": False
                    })
                elif "pension" in description.lower() or "retirement" in description.lower():
                    transactions.append({
                        "date": date_str,
                        "description": description,
                        "amount": amount,
                        "category": "income",
                        "is_refund": False
                    })
                # Skip ATM deposits, counter credits, transfers, etc.
            except ValueError:
                continue

    # Also collect SKIPPED transactions for audit trail
    skipped_transactions = []

    # Re-process to capture skipped items
    for header_idx in header_indices:
        i = header_idx + 1

        while i < len(all_lines):
            line = all_lines[i].strip()

            if re.search(r'Total|continued on|Checks', line, re.IGNORECASE):
                break

            date_match = re.match(r'^(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+)', line)

            if date_match:
                date_str = date_match.group(1)
                rest_of_line = date_match.group(2).strip()
                amount_match = re.search(r'(-[\d,]+\.\d{2})\s*$', rest_of_line)

                if amount_match:
                    amount_str = amount_match.group(1).replace(",", "")
                    description = rest_of_line[:amount_match.start()].strip()

                    try:
                        amount = float(amount_str)
                        description = " ".join(description.split())
                        if len(description) > 100:
                            description = description[:100] + "..."

                        category, is_skip, is_refund = categorize_transaction(description, amount)

                        # If skipped, add to skipped list
                        if is_skip:
                            skipped_transactions.append({
                                "date": date_str,
                                "description": description,
                                "amount": amount,
                                "reason": category  # e.g., "credit_card_payment", "atm", etc.
                            })
                    except ValueError:
                        pass

                    i += 1
                else:
                    # Multi-line - skip for now in this pass
                    i += 1
            else:
                i += 1

    return {
        "account": account_number,
        "period_start": start_date,
        "period_end": end_date,
        "transactions": transactions,
        "total_transactions": len(transactions),
        "skipped_transactions": skipped_transactions,
        "total_skipped": len(skipped_transactions)
    }


# ============================================================================
# WORD DOCUMENT PARSING
# ============================================================================

def extract_text_from_docx(docx_file) -> str:
    """Extract text from Word document"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")

    try:
        doc = DocxDocument(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting Word document text: {e}")
        return ""


def parse_financial_document_docx(docx_file) -> Dict:
    """Parse financial information from Word document"""
    text = extract_text_from_docx(docx_file)

    if not text:
        return {"error": "Could not extract text from Word document"}

    # Look for income/expense patterns
    data = {
        "income": {},
        "expenses": {},
        "raw_text": text
    }

    # Pattern: Category: $amount
    pattern = r"([A-Za-z\s]+):\s*\$?([\d,]+\.?\d{0,2})"

    for match in re.finditer(pattern, text):
        label = match.group(1).strip().lower()
        amount_str = match.group(2).replace(",", "")

        try:
            amount = float(amount_str)

            # Categorize as income or expense
            is_income = any(kw in label for kw in ["income", "salary", "wage", "pension", "social security"])

            if is_income:
                data["income"][label] = amount
            else:
                # Try to map to expense category
                category = "miscellaneous"
                for cat, keywords in EXPENSE_CATEGORIES.items():
                    if any(kw in label for kw in keywords) or cat in label:
                        category = cat
                        break
                data["expenses"][category] = data["expenses"].get(category, 0) + amount

        except ValueError:
            continue

    return data


# ============================================================================
# IMAGE OCR PARSING
# ============================================================================

def extract_text_from_image(image_file) -> str:
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        st.warning("⚠️ OCR not available. Install with: pip install pytesseract pillow")
        st.info("Also install Tesseract: https://github.com/tesseract-ocr/tesseract")
        return ""

    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error performing OCR: {e}")
        return ""


def parse_receipt_image(image_file) -> Dict:
    """Parse a receipt or statement image using OCR"""
    text = extract_text_from_image(image_file)

    if not text:
        return {"error": "Could not extract text from image"}

    # Look for total amount
    total_pattern = r"Total:?\s*\$?([\d,]+\.?\d{0,2})"
    total_match = re.search(total_pattern, text, re.IGNORECASE)
    total = float(total_match.group(1).replace(",", "")) if total_match else 0.0

    # Look for merchant name (usually at top)
    lines = text.split("\n")
    merchant = lines[0].strip() if lines else "Unknown Merchant"

    # Try to categorize
    category, _, _ = categorize_transaction(text, -total)

    return {
        "merchant": merchant,
        "total": total,
        "category": category,
        "raw_text": text
    }


# ============================================================================
# MONTH NORMALIZATION & PRORATION (GROK's Rule #1)
# ============================================================================

def prorate_amount_by_days(amount: float, start_date: datetime, end_date: datetime, target_month: int, target_year: int) -> float:
    """
    Prorate an amount to a specific calendar month based on how many days fall in that month.

    Example: $120 bill for 08/10–09/09 (31 days)
    - August portion (08/10–08/31 = 22 days): 120 × (22/31) = $85.16
    - September portion (09/01–09/09 = 9 days): 120 × (9/31) = $34.84
    """
    # Find first and last day of target month
    from calendar import monthrange

    _, days_in_month = monthrange(target_year, target_month)
    month_start = datetime(target_year, target_month, 1)
    month_end = datetime(target_year, target_month, days_in_month)

    # Find overlap between statement period and target month
    overlap_start = max(start_date, month_start)
    overlap_end = min(end_date, month_end)

    if overlap_start > overlap_end:
        return 0.0  # No overlap

    days_in_overlap = (overlap_end - overlap_start).days + 1
    total_days = (end_date - start_date).days + 1

    prorated = amount * (days_in_overlap / total_days)
    return round(prorated, 2)


# ============================================================================
# ROBUST BASELINE CALCULATION (GROK's Rule #2)
# ============================================================================

def calculate_robust_baseline(monthly_amounts: List[float], method: str = "median", category: str = "miscellaneous") -> Tuple[float, float]:
    """
    Calculate a robust monthly baseline from a list of amounts.

    Methods:
    - "median": Median of values (preferred, resists outliers)
    - "smart_mode": Finds most common recurring amount (best for bills/rent)
    - "emwa": Exponential Moving Weighted Average (α=0.3)
    - "winsorized_median": Median after capping outliers at 3× rolling median

    Returns: (baseline_amount, confidence_score)
    """
    if not monthly_amounts:
        return 0.0, 0.0

    # Remove None values
    amounts = [a for a in monthly_amounts if a is not None]

    if not amounts:
        return 0.0, 0.0

    # For recurring bills (housing, utilities, insurance), use SMART MODE
    # This finds the most common LARGE payment, not just median of all values
    recurring_categories = ["housing", "utilities", "insurance", "subscriptions"]

    if category in recurring_categories and len(amounts) >= 3:
        # Filter out very small transactions (likely mis-categorized or fees)
        # Keep only amounts above 10th percentile
        sorted_amounts = sorted(amounts)
        threshold_idx = max(0, int(len(sorted_amounts) * 0.1))  # 10th percentile
        large_amounts = sorted_amounts[threshold_idx:]

        if large_amounts:
            # Find mode (most common value) with 10% tolerance
            # Group similar amounts together (within 10% of each other)
            from collections import defaultdict
            clusters = defaultdict(list)

            for amt in large_amounts:
                # Find existing cluster within 10% range
                found_cluster = False
                for cluster_key in list(clusters.keys()):
                    if abs(amt - cluster_key) / max(amt, cluster_key) < 0.10:
                        clusters[cluster_key].append(amt)
                        found_cluster = True
                        break

                if not found_cluster:
                    clusters[amt] = [amt]

            # Find largest cluster (most common payment amount)
            if clusters:
                largest_cluster_key = max(clusters.items(), key=lambda x: len(x[1]))[0]
                largest_cluster = clusters[largest_cluster_key]

                # Use mean of the largest cluster as baseline
                baseline = sum(largest_cluster) / len(largest_cluster)
                confidence = min(1.0, len(largest_cluster) / 3.0)  # Full confidence at 3+ same payments
                return baseline, confidence

    # Default: Use median for all other cases
    if method == "median":
        baseline = median(amounts)
        confidence = min(1.0, len(amounts) / 6.0)  # Full confidence at 6+ months
        return baseline, confidence

    elif method == "emwa":
        # Exponential Moving Weighted Average with α=0.3
        alpha = 0.3
        emwa = amounts[0]
        for amount in amounts[1:]:
            emwa = alpha * amount + (1 - alpha) * emwa
        confidence = min(0.9, len(amounts) / 6.0)  # Max 0.9 for EMWA
        return emwa, confidence

    elif method == "winsorized_median":
        # Cap outliers at 3× median before taking median
        initial_median = median(amounts)
        cap = 3 * initial_median
        winsorized = [min(a, cap) for a in amounts]
        baseline = median(winsorized)
        confidence = min(1.0, len(amounts) / 6.0)
        return baseline, confidence

    return 0.0, 0.0


# ============================================================================
# CONFIDENCE SCORING (GROK's Rule #7)
# ============================================================================

def calculate_confidence(
    num_months: int,
    has_partial: bool,
    used_allocation: bool,
    used_default: bool
) -> float:
    """
    Calculate confidence score for a baseline estimate.

    Scoring:
    1.00 = ≥3 full months, median used, no outliers
    0.90 = partial months with clean proration; EMWA minimal
    0.75 = allocation from card totals by historical mix
    0.60 = seasonal backfill without current neighbors
    0.40 = anchored default/benchmark due to no data
    """
    if used_default:
        return 0.40

    if used_allocation:
        return 0.75

    if has_partial:
        return 0.90

    if num_months >= 3:
        return 1.00
    elif num_months >= 2:
        return 0.90
    elif num_months >= 1:
        return 0.75
    else:
        return 0.60


# ============================================================================
# CATEGORY-SPECIFIC LOGIC (GROK's Rule #3)
# ============================================================================

def handle_mortgage_specific(payment_amount: float, interest_rate: float, balance: float) -> Dict:
    """
    Handle mortgage-specific logic.
    Never impute from spend—use amortization schedule.
    """
    monthly_interest = (balance * (interest_rate / 100)) / 12
    principal = payment_amount - monthly_interest

    return {
        "total_payment": payment_amount,
        "principal": max(0, principal),
        "interest": monthly_interest,
        "confidence": 1.0 if balance > 0 else 0.6
    }


def handle_annual_bill(single_payment: float, bill_type: str) -> Dict:
    """
    Handle annual/semi-annual bills (property tax, insurance, etc.)
    When one payment is seen, annualize → /12 and carry monthly.
    """
    monthly_amount = single_payment / 12

    return {
        "bill_type": bill_type,
        "annual_amount": single_payment,
        "monthly_amount": round(monthly_amount, 2),
        "confidence": 0.90  # Good confidence from actual bill
    }


def handle_subscription(amounts: List[float]) -> Dict:
    """
    Handle subscription payments.
    If all months are identical, carry forward exact amount.
    """
    if not amounts:
        return {"monthly_amount": 0.0, "confidence": 0.0}

    unique_amounts = set(amounts)

    if len(unique_amounts) == 1:
        # Identical every month - perfect!
        return {"monthly_amount": amounts[0], "confidence": 1.0}
    else:
        # Some variation - use median
        return {"monthly_amount": median(amounts), "confidence": 0.85}


# ============================================================================
# EXPORT & FORMATTING
# ============================================================================

def export_to_intake_format(parsed_data: Dict, smoothing: str = "exact") -> Dict:
    """
    Convert parsed document data to INTAKE app format.

    Smoothing options:
    - "exact": No rounding (default)
    - "light": Round utilities/subs to nearest $10-25
    - "discretionary": Round food/dining to nearest $50
    """
    intake_data = {}

    # Income fields
    if "income" in parsed_data:
        for income_type, amount in parsed_data["income"].items():
            # Map to intake field names
            if "salary" in income_type or "wage" in income_type:
                intake_data["input_salary_wages"] = amount
            elif "social security" in income_type:
                intake_data["input_social_security_income"] = amount
            elif "pension" in income_type:
                intake_data["input_pension_income"] = amount
            # Add more mappings as needed

    # Expense fields
    if "expenses" in parsed_data:
        for category, amount in parsed_data["expenses"].items():
            # Apply smoothing if requested
            if smoothing == "light" and category in ["utilities"]:
                amount = round(amount / 10) * 10  # Nearest $10
            elif smoothing == "discretionary" and category in ["groceries", "dining"]:
                amount = round(amount / 50) * 50  # Nearest $50

            # Map to intake field names
            category_map = {
                "housing": "input_housing_expenses",
                "utilities": "input_utilities_expenses",
                "groceries": "input_groceries_expenses",
                "dining": "input_restaurant_expenses",
                "transportation": "input_transportation_expenses",
                "healthcare": "input_healthcare_expenses",
                "insurance": "input_insurance_expenses",
                "entertainment": "input_entertainment_expenses",
                "travel": "input_travel_expenses",
                "miscellaneous": "input_miscellaneous_expenses"
            }

            field_name = category_map.get(category, "input_other_expenses")
            intake_data[field_name] = amount

    # Add confidence scores
    if "confidence_by_field" in parsed_data:
        intake_data["_confidence_scores"] = parsed_data["confidence_by_field"]

    return intake_data


# ============================================================================
# MAIN PARSING FUNCTION
# ============================================================================

def parse_uploaded_document(uploaded_file, debug=False) -> Dict:
    """
    Main entry point for parsing any uploaded document.
    Auto-detects file type and routes to appropriate parser.

    Returns structured data ready for INTAKE app.
    """
    if uploaded_file is None:
        return {"error": "No file uploaded"}

    file_name = uploaded_file.name.lower()
    file_type = uploaded_file.type

    try:
        if file_name.endswith('.pdf') or 'pdf' in file_type:
            return parse_bank_statement_pdf(uploaded_file, debug=debug)

        elif file_name.endswith('.docx') or 'word' in file_type:
            return parse_financial_document_docx(uploaded_file)

        elif file_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')) or 'image' in file_type:
            return parse_receipt_image(uploaded_file)

        else:
            return {"error": f"Unsupported file type: {file_name}"}

    except Exception as e:
        return {"error": f"Error parsing document: {str(e)}"}
