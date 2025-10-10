from dataclasses import dataclass
from typing import List, Dict, Optional

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
    out = []
    for r in children_rows:
        if not r: 
            continue
        name = str(r.get("Name", "")).strip()
        if not name:
            continue
        try:
            by = int(r.get("Birth Year"))
        except Exception:
            continue
        plan_raw = str(r.get("College Plan", "None")).strip().lower()
        plan_map = {
            "none": "none", "no": "none", "": "none",
            "public in-state": "public_in",
            "public out-of-state": "public_out",
            "private nonprofit": "private",
            "private": "private"
        }
        plan_type = plan_map.get(plan_raw, "none")
        sch = float(r.get("Scholarship %", 0.0)) if r.get("Scholarship %", "") != "" else 0.0
        use_529 = bool(r.get("Use 529 First?", True))
        out.append(Child(
            name=name,
            birth_year=by,
            college=CollegePlan(plan_type=plan_type,
                                start_age=int(r.get("Start Age", 18) or 18),
                                years=int(r.get("Years", 4) or 4),
                                scholarship_pct=max(0.0, min(100.0, sch)),
                                use_529_first=use_529)
        ))
    return out

def build_inheritances(events_rows: List[dict]) -> List[InheritanceEvent]:
    evs = []
    for r in events_rows:
        if not r:
            continue
        try:
            y = int(r.get("Year"))
            amt = float(r.get("Amount"))
            if amt == 0:
                continue
            taxable = bool(r.get("Taxable?", False))
            evs.append(InheritanceEvent(year=y, amount=amt, taxable=taxable))
        except Exception:
            continue
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