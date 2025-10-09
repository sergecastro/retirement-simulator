# household_events.py — Family event processing (compat+robust parsing)
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

# NOTE TO MAINTAINERS:
# This module is now tolerant of multiple intake schemas:
# - Children rows: accepts "Name"/"name", "Birth Year"/"birth_year", "College Plan"/"college_plan",
#   "Scholarship %"/"scholarship_pct", "Use 529 First?"/"use_529_first"/"use_529",
#   "Start Age"/"start_age", "Years"/"years".
#   We REQUIRE a name and a birth year (cannot safely derive from "Age" without user age).
# - Inheritances: accepts "Year"/"year" OR "Amount"/"amount" OR "Taxable?"/"taxable"/"is_taxable".
#   (Age-at-receipt only is not supported here because it needs user age; if present without Year, we skip.)
#
# Public API is unchanged:
#   build_child_objects(children_rows: List[dict]) -> List[Child]
#   build_inheritances(events_rows: List[dict]) -> List[InheritanceEvent]
#   make_family_cashflows(...)
#
# If you later want to support "Age at Receipt" -> Year conversion, do it in the INTAKE layer where
# you know current year and the user’s age, and write a proper "Year" into the payload.

@dataclass
class CollegePlan:
    plan_type: str           # "none" | "public_in" | "public_out" | "private"
    start_age: int = 18
    years: int = 4
    scholarship_pct: float = 0.0   # 0..100
    use_529_first: bool = True

@dataclass
class Child:
    name: str
    birth_year: int
    college: CollegePlan

@dataclass
class InheritanceEvent:
    year: int
    amount: float           # treated as after-tax inflow into taxable assets
    taxable: bool = False   # optional flag (not used in simple model)

# ---------- helpers ----------
def _get(row: Dict[str, Any], *keys, default=None):
    """Return first non-None/non-'' value for any of keys (order matters)."""
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return default

def _to_int(val, default: Optional[int] = None) -> Optional[int]:
    try:
        if val is None or val == "":
            return default
        return int(val)
    except Exception:
        return default

def _to_float(val, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        # Handle strings like "$5,555"
        if isinstance(val, str):
            v = val.replace("$", "").replace(",", "").strip()
            return float(v) if v else default
        return float(val)
    except Exception:
        return default

def _to_bool(val, default: bool = False) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        s = val.strip().lower()
        if s in ("true", "yes", "y", "1", "on"):
            return True
        if s in ("false", "no", "n", "0", "off"):
            return False
    return default

# ---------- public API ----------
def college_annual_cost(plan_type: str,
                        base_public_in: float,
                        base_public_out: float,
                        base_private: float) -> float:
    if plan_type == "public_in":
        return float(base_public_in)
    if plan_type == "public_out":
        return float(base_public_out)
    if plan_type == "private":
        return float(base_private)
    return 0.0

def build_child_objects(children_rows: List[dict]) -> List[Child]:
    """
    Robustly parse children rows from intake.
    Requires: name + birth_year
    Accepts schema variants and normalizes college plan values.
    """
    out: List[Child] = []
    if not isinstance(children_rows, list):
        return out

    plan_map = {
        "none": "none", "no": "none", "": "none",
        "public in-state": "public_in", "public instate": "public_in", "in-state": "public_in",
        "public out-of-state": "public_out", "public outofstate": "public_out", "out-of-state": "public_out",
        "private nonprofit": "private", "private": "private"
    }

    for r in children_rows:
        if not isinstance(r, dict) or not r:
            continue

        # Name (required)
        name = _get(r, "Name", "name", "child_name", default="")
        name = str(name).strip()
        if not name:
            continue

        # Birth Year (required; we do NOT derive from "Age")
        birth_year = _to_int(_get(r, "Birth Year", "birth_year"), default=None)
        if birth_year is None:
            # as a courtesy, try "BirthYear"
            birth_year = _to_int(_get(r, "BirthYear"), default=None)
        if birth_year is None:
            # cannot proceed without a concrete year anchor
            continue

        # College plan (optional; default none)
        plan_raw = str(_get(r, "College Plan", "college_plan", default="none")).strip().lower()
        plan_type = plan_map.get(plan_raw, "none")

        # Scholarship %
        scholarship_pct = _to_float(_get(r, "Scholarship %", "scholarship_pct"), default=0.0)
        scholarship_pct = max(0.0, min(100.0, scholarship_pct))

        # Use 529 First?
        use_529_first = _to_bool(_get(r, "Use 529 First?", "use_529_first", "use_529"), default=True)

        # Start Age / Years
        start_age = _to_int(_get(r, "Start Age", "start_age"), default=18)
        years = _to_int(_get(r, "Years", "years"), default=4)

        out.append(Child(
            name=name,
            birth_year=birth_year,
            college=CollegePlan(
                plan_type=plan_type,
                start_age=start_age,
                years=years,
                scholarship_pct=scholarship_pct,
                use_529_first=use_529_first
            )
        ))
    return out

def build_inheritances(events_rows: List[dict]) -> List[InheritanceEvent]:
    """
    Build inheritance events with tolerant schema handling:
      • Year: accepts 'Year' or 'year'
      • Amount: accepts 'Amount' or 'amount' (currency strings ok)
      • Taxable flag: 'Taxable?' or 'taxable' or 'is_taxable'
    NOTE: If only 'Age at Receipt' is present and no 'Year', we SKIP (needs user age for conversion).
    """
    evs: List[InheritanceEvent] = []
    if not isinstance(events_rows, list):
        return evs

    for r in events_rows:
        if not isinstance(r, dict) or not r:
            continue

        y = _to_int(_get(r, "Year", "year"), default=None)
        # If no concrete year is provided, we cannot schedule the event here (skip).
        if y is None:
            # Graceful skip; upstream should have converted "Age at Receipt" to a calendar year
            # before reaching this layer.
            continue

        amt = _to_float(_get(r, "Amount", "amount"), default=0.0)
        if amt <= 0:
            continue

        taxable = _to_bool(_get(r, "Taxable?", "taxable", "is_taxable"), default=False)
        evs.append(InheritanceEvent(year=y, amount=amt, taxable=taxable))

    return evs

def make_family_cashflows(children: List[Child],
                          inheritances: List[InheritanceEvent],
                          start_year: int,
                          horizon_end: int,
                          college_inflation_pct: float,
                          base_public_in: float,
                          base_public_out: float,
                          base_private: float) -> Dict[int, Dict[str, float]]:
    """
    Returns dict: {year: { 'expense_delta': +x, 'inflow_delta': +y }}
    - college costs are added as expense_delta (positive)
    - inheritance amounts added as inflow_delta (positive)
    """
    out: Dict[int, Dict[str, float]] = {}

    def bump(y: int, key: str, amt: float):
        if y < start_year or y > horizon_end:
            return
        if y not in out:
            out[y] = {"expense_delta": 0.0, "inflow_delta": 0.0}
        out[y][key] += amt

    # Children → college cashflows
    for ch in children:
        if ch.college.plan_type == "none":
            continue
        # compute college start/end years
        cs = ch.birth_year + max(0, ch.college.start_age)
        ce = cs + max(0, ch.college.years)
        # Clamp to horizon
        s2 = max(start_year, cs)
        e2 = min(horizon_end, ce)
        cost0 = college_annual_cost(ch.college.plan_type, base_public_in, base_public_out, base_private)
        if cost0 <= 0:
            continue
        for y in range(s2, e2):
            t = y - cs  # years since start for inflation compounding
            gross = cost0 * ((1.0 + college_inflation_pct/100.0) ** max(0, t))
            net = gross * (1.0 - ch.college.scholarship_pct/100.0)
            bump(y, "expense_delta", max(0.0, net))

    # Inheritances → inflows
    for ev in inheritances:
        if start_year <= ev.year <= horizon_end:
            bump(ev.year, "inflow_delta", max(0.0, ev.amount))

    return out
