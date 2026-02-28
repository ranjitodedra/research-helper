# Energy Calculation Discrepancy Analysis

## Problem
Two different implementations of the same energy consumption formula are producing different results:
- `energy.py` (EVRP-SCS-and-DWC-Genetic-Algorithm): 7.4245 kWh
- `UIG/uig.py` (via `input_generator.py`): 7.59 kWh

## Root Causes

### 1. **CRITICAL BUG: Speed Conversion Error in energy.py**

**Location**: `energy.py` lines 68-73

**Issue**: The code converts speed from km/h to m/s, but then uses a constant (0.0386) that is designed for km/h.

```python
# energy.py (WRONG)
v_ms = speed_kmh / 3.6                  # Convert to m/s
aero = 0.0386 * (rho * Cx * A * (v_ms ** 2))  # Uses 0.0386 with m/s - WRONG!
```

**Correct approach** (as in `input_generator.py`):
```python
# input_generator.py (CORRECT)
v0 = base_speed * traffic_factor  # Keep in km/h
aero = 0.0386 * (p * c * A * v0**2)  # Use 0.0386 with km/h - CORRECT!
```

**Why this matters**: 
- The constant `0.0386 ≈ 1/(3.6²) × 0.5` is designed to work with km/h
- When used with m/s, it produces aerodynamic drag that is ~13× smaller than it should be
- This causes significant underestimation of energy consumption

### 2. **Different Parameter Values**

| Parameter | input_generator.py (UIG) | energy.py (EVRP) | Impact |
|-----------|-------------------------|------------------|--------|
| Vehicle Mass (M) | 1530 kg | 1800 kg | Higher mass = more energy |
| Mass Factor (m) | 100 kg | 1.1 kg | Affects acceleration term |
| Drag Coefficient (Cx) | 0.3 | 0.6 | Higher drag = more energy |
| Cross-sectional Area (A) | 2.5 m² | 3.5 m² | Larger area = more drag |

### 3. **Unit Conversion Differences**

**input_generator.py**:
- Distance: uses `d` directly in km
- Speed: uses `v0` in km/h
- Formula: `E = (1/3600) * [force] * d` where d is in km
- Result: Energy in kWh (implicit conversion)

**energy.py**:
- Distance: converts to meters `d_m = distance_km * 1000`
- Speed: converts to m/s `v_ms = speed_kmh / 3.6` (but uses wrong constant)
- Formula: `E = (1/3600) * [force] * d_m / 1000`
- Result: Energy in kWh (explicit conversion)

## Mathematical Verification

For a test case with distance = 5 km, speed = 50 km/h:

### input_generator.py (CORRECT):
```
v0 = 50 km/h
aero = 0.0386 * (1.205 * 0.3 * 2.5 * 50²) = 87.0 N
```

### energy.py (WRONG):
```
v_ms = 50/3.6 = 13.89 m/s
aero = 0.0386 * (1.205 * 0.6 * 3.5 * 13.89²) = 18.8 N  ← Too small!
```

### energy.py (CORRECTED):
```
v_ms = 50/3.6 = 13.89 m/s
aero = 0.5 * (1.205 * 0.6 * 3.5 * 13.89²) = 244.1 N  ← Correct!
```

## Recommendations

### Fix 1: Correct the speed conversion in energy.py

**Option A** (Recommended): Keep speed in km/h
```python
# In energy.py, line 68-73
v_kmh = speed_kmh  # Keep in km/h
d_m = distance_km * 1000

rolling = M * g * (f * math.cos(alpha) + math.sin(alpha))
aero = 0.0386 * (rho * Cx * A * (v_kmh ** 2))  # Use km/h
accel = (M + mass_factor) * dv_dt

energy_wh = (1.0 / 3600.0) * (rolling + aero + accel) * d_m
energy_kwh = energy_wh / 1000.0
```

**Option B**: Use m/s with correct constant
```python
v_ms = speed_kmh / 3.6
d_m = distance_km * 1000

rolling = M * g * (f * math.cos(alpha) + math.sin(alpha))
aero = 0.5 * (rho * Cx * A * (v_ms ** 2))  # Use 0.5 for m/s
accel = (M + mass_factor) * dv_dt

energy_wh = (1.0 / 3600.0) * (rolling + aero + accel) * d_m
energy_kwh = energy_wh / 1000.0
```

### Fix 2: Standardize parameter values

Decide on a single set of standard parameters to use across both implementations.

## Impact

The speed conversion bug in `energy.py` causes:
- Underestimation of aerodynamic drag by ~13×
- Overall energy consumption underestimation
- Inconsistent results between implementations

The parameter differences cause additional variation, but the speed conversion bug is the primary issue.
