# Commands

## Base case
```
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.2
```

## E-road ratio
```
# ER −25% (er = 0.15)
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.15

# ER +25% (er = 0.25)
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.25

# ER +50% (er = 0.30)
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.30
```

## CS ratio variations
```
# CS −25% (cs = 0.15) → ~4 BSS nodes
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.2 --cs-ratio 0.15

# CS +25% (cs = 0.25) → ~7 BSS nodes
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.2 --cs-ratio 0.25

# CS +50% (cs = 0.30) → ~8 BSS nodes
python UIG2\uig2.py 28 --seed 799 --eroad-ratio 0.2 --cs-ratio 0.30
```

