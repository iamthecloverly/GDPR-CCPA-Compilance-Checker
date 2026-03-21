# Design & Development Lessons

Lessons learned from bugs and mistakes in this project. Reference this before implementing UI or data-driven features.

---

## 1. Design from Data Inward, Not UI Outward

**Mistake:** Designed category cards with hardcoded category names (`"Trackers (0=best)"`) without checking what the controller actually generates.

**Reality:** Controller builds keys dynamically: `f"Trackers ({len(trackers)} found)"` → `"Trackers (0 found)"`, `"Trackers (3 found)"`, etc.

**Result:** Card key lookup always returned 0, showing wrong score.

**Rule:**
- Always trace data flow: Controller → Results dict → Display
- Read the actual controller output format before designing the UI
- Verify keys/values in `controllers/compliance_controller.py` match your display assumptions

**Example:**
```python
# WRONG: Hardcoded key
pts = breakdown.get("Trackers (0=best)", 0)

# RIGHT: Dynamic lookup by pattern
tracker_key = next((k for k in breakdown if k.startswith("Trackers")), None)
pts = breakdown.get(tracker_key, 0)
```

---

## 2. Never Hardcode Constants — Read from Config

**Mistake:** Assumed all score categories had max=30 points. Reality: Contact Info=20, Trackers=20.

**Location:** `config.py` defines `SCORING_WEIGHTS`:
- `cookie_consent`: 30
- `privacy_policy`: 30
- `contact_info`: 20
- `trackers`: 20

**Result:** Display showed wrong max (30 instead of 20), made scoring impossible to fix without touching code.

**Rule:**
- Check `config.py` for all numeric constants before hardcoding
- Derive max_pts from `Config.SCORING_WEIGHTS` instead of assuming
- Don't hardcode category names — they may change via env vars

**Example:**
```python
# WRONG
max_pts = 30  # hardcoded

# RIGHT
from config import Config
max_pts = Config.SCORING_WEIGHTS.get("contact_info", 20)
```

---

## 3. Users Need Context, Not Just Numbers

**Mistake:** Showed "0/30 Issues found" with no explanation of what the issues are.

**Rule:**
- Always pair a metric with a reason/explanation
- Show one-line context snippets inline (not in a separate section below)
- For compliance data: show what was missing/detected, not just the score

**Pattern in this codebase:**
- `results["cookie_consent"]`: e.g., `"Found cookie banner at /policies"` or `"Not Found - no consent mechanism detected"`
- `results["privacy_policy"]`: similar
- `results["contact_info"]`: similar
- `results["trackers"]`: list of domain names

**Implementation:**
```python
# In render_quick_results(), add reason to each card
reason = str(results.get("cookie_consent", ""))[:70]
st.markdown(f"**Reason:** {reason}")
```

---

## 4. Use Dynamic Lookups, Not Exact Key Matches

**Mistake:** Hardcoded `breakdown.get("Trackers (0=best)", 0)` failed because actual key is `"Trackers (3 found)"`.

**Rule:**
- When a key might vary, search for it by pattern, prefix, or ID
- Use `next((k for k in dict if predicate(k)), default)` for finding by pattern
- Document why the key is dynamic in a comment

**Example:**
```python
# WRONG: Exact match fails
tracker_key = "Trackers (0=best)"  # never matches actual data
pts = breakdown.get(tracker_key, 0)  # always returns 0

# RIGHT: Pattern-based lookup
tracker_key = next(
    (k for k in breakdown if k.startswith("Trackers")),
    None
)
pts = breakdown.get(tracker_key, 0) if tracker_key else 0
```

---

## 5. Handle Legacy Data Gracefully

**Mistake:** Old DB rows stored trackers as Python repr strings (`"['google.com', 'facebook.net']"`) instead of JSON. Code did `json.loads(raw)` and crashed on those rows.

**Rule:**
- Add fallback deserializers for old/legacy data formats
- Don't assume all historical data matches the new schema
- Use try/except with `ast.literal_eval()` as a fallback for Python repr strings

**Implementation in `database/operations.py`:**
```python
def _parse_trackers(raw: Any) -> list:
    """Safely parse trackers — handles both JSON and legacy Python-repr strings."""
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Legacy: stored as Python repr "['google.com', 'facebook.net']"
        try:
            val = ast.literal_eval(raw)
            return val if isinstance(val, list) else []
        except Exception:
            return []
```

---

## 6. Test Actual Output, Not Assumptions

**Mistake:** Card showed `0/30` but I didn't immediately debug *why*. Should have inspected the breakdown dict.

**Rule:**
- When output looks wrong, print/inspect the data immediately
- Don't assume the data matches your model
- Add a quick debug: `st.write(breakdown)` or `logger.info(breakdown)` to verify

**Pattern:**
```python
# Add debug logging when data doesn't match expectations
breakdown = results.get("score_breakdown", {})
logger.info(f"Breakdown keys: {list(breakdown.keys())}")  # reveals key mismatch
```

---

## 7. Category Max Points Mapping

Keep this reference for scoring constants. From `config.py`:

| Category | Max Points | Key in breakdown |
|----------|-----------|-----------------|
| Cookie Consent | 30 | `"Cookie Consent"` |
| Privacy Policy | 30 | `"Privacy Policy"` |
| Contact Info | 20 | `"Contact Info"` |
| Trackers | 20 | `"Trackers (X found)"` (dynamic) |

**Total max:** 100 points

---

## Checklist Before Implementing UI Features

- [ ] Read the controller output format (`controllers/compliance_controller.py`)
- [ ] Check `config.py` for all constants and weights
- [ ] Verify what keys are in the results dict
- [ ] If keys are dynamic, use `next()` pattern matching, not exact matches
- [ ] Add one-line reason/context snippets alongside metrics
- [ ] Test with actual data, not hardcoded examples
- [ ] Add fallback deserializers for legacy data
- [ ] Document why keys or values are dynamic in comments

---

## Related Files

- `controllers/compliance_controller.py` — defines score breakdown structure
- `config.py` — `SCORING_WEIGHTS` constants
- `database/operations.py` — data deserialization patterns
- `components/results_display.py` — UI display patterns
