# UIG2

`UIG2` is a separate generator for project 2 inputs. It does not modify `UIG`.

It generates:
- GA JSON compatible with `EVRP-SCS-and-DWC-Genetic-Algorithm`
- DAT compatible with `CPLEX-Project-2/E_Road.mod`
- A short summary text file
- A graph PNG (best effort)

## Usage

From repository root:

```powershell
python UIG2\uig2.py 24 --seed 42 --electric-ratio 0.2
```

Arguments:
- `total_nodes` (required): total node count, minimum 4
- `--seed` (optional): random seed for deterministic generation
- `--electric-ratio` (optional): ratio of eligible edges marked electric, range `[0, 1]`

## Output Files

Files are written into `UIG2/` using:

`{customers}c_{bss}bss_{total}total.*`

Generated artifacts:
- `.json` (GA instance)
- `.dat` (CPLEX input)
- `_example.txt` (summary)
- `.png` (network visualization, if plotting dependencies are available)

## Schema Notes

### GA JSON
- Node mapping:
  - `D` -> depot
  - `C*` -> `L*` customer
  - `BSS*` -> `CS*` charging station
  - numeric labels remain intersections
- Edge mapping:
  - normal edges are stored as a single directed entry
  - electric edges are single-direction (`from` -> `to`) with `type: "electric"`
  - electric edges use `traffic_factor: 1.0` to align with constant e-road speed

### CPLEX DAT
Includes all arrays required by `E_Road.mod`:
- `Adj`, `Dist`, `Trav`, `Edep`, `Ebox`, `Eroad`
- scalar parameters: `Initial`, `Eth`, `S`, `D`, `G`, `Nodes`, `Visits`, `ECharging`, `Reroad`
- vectors: `Station`, `Costumer`

## DWC Formula Alignment

This generator includes the fields used by the GA simulator for DWC:
- `dwc_power`
- `dwc_efficiency`
- `electric_road_speed`

The simulator applies:

`E_DWC = P_chg * eta_chg * (L_DWC / v)`

## Dependency Fallback

`archive/NetworkGenerator` uses KMeans for BSS placement and may require
`numpy` + `scikit-learn`. If those are not installed, `UIG2` uses an internal
fallback topology builder so generation still succeeds.
