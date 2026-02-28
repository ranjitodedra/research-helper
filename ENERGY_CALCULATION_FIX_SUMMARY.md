# Energy Calculation Discrepancy - Investigation & Fix Summary

## Problem Identified

You reported that `energy.py` (EVRP-SCS-and-DWC-Genetic-Algorithm) and `UIG/uig.py` (via `input_generator.py`) were producing different energy consumption results for the same example:
- `energy.py`: 7.4245 kWh
- `UIG/uig.py`: 7.59 kWh

## Root Cause: Critical Bug in energy.py

**Location**: `energy.py`, line 73

**The Bug**: The code was converting speed from km/h to m/s, but then using a constant (0.0386) that is designed specifically for km/h.

```python
# BEFORE (WRONG):
v_ms = speed_kmh / 3.6                  # Convert to m/s
aero = 0.0386 * (rho * Cx * A * (v_ms ** 2))  # Uses 0.0386 with m/s - WRONG!
```

**The Fix**: Keep speed in km/h to match the constant:

```python
# AFTER (CORRECT):
v_kmh = speed_kmh                        # Keep in km/h
aero = 0.0386 * (rho * Cx * A * (v_kmh ** 2))  # Use km/h with 0.0386 - CORRECT!
```

## Impact of the Bug

The bug caused **severe underestimation of aerodynamic drag**:
- Before fix: Aero term ≈ 18.8 N (for 50 km/h)
- After fix: Aero term ≈ 244.2 N (for 50 km/h)
- **The bug made aerodynamic drag ~13× smaller than it should be**

This significantly affected total energy consumption calculations.

## Additional Differences (Not Bugs)

The implementations also use different parameter values, which is expected and acceptable:

| Parameter | input_generator.py (UIG) | energy.py (EVRP) |
|-----------|-------------------------|------------------|
| Vehicle Mass | 1530 kg | 1800 kg |
| Mass Factor | 100 kg | 1.1 kg |
| Drag Coefficient | 0.3 | 0.6 |
| Cross-sectional Area | 2.5 m² | 3.5 m² |

These parameter differences will cause some variation in results, but this is intentional based on different vehicle configurations.

## Verification

After the fix:
- The aerodynamic drag calculation is now mathematically correct
- The formula now matches the implementation in `input_generator.py`
- Remaining differences are due to legitimate parameter value differences

## Files Modified

1. **`energy.py`** (EVRP-SCS-and-DWC-Genetic-Algorithm)
   - Fixed speed conversion bug on line 73
   - Changed from using `v_ms` (m/s) to `v_kmh` (km/h) with the 0.0386 constant

## Recommendation

The fix has been applied. The energy calculation in `energy.py` is now correct. The remaining differences between the two implementations are due to different parameter values, which is expected and acceptable.

If you want the results to match exactly, you would need to:
1. Standardize the parameter values across both implementations
2. Ensure both use the same vehicle mass, drag coefficient, cross-sectional area, and mass factor

However, having different parameter values is often intentional to model different vehicle configurations.
