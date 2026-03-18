# How to Run the Traffic Modifier
```
python modify_traffic.py \
  --dat path/to/file.dat \
  --json path/to/file_V3.json \
  --lower 0.6 --upper 0.9 \
  --seed 42 \
  --output-dir path/to/output/
```

Traffic | Traffic-Factor
------------------------
Low     | 0.6 - 0.73
Mid     | 0.73 - 0.87
High    | 0.87 - 1.0


## Low Traffic
```
python modify_traffic.py --dat path/to/file.dat --json path/to/file_V3.json --lower 0.87 --upper 1.0 --seed 42 --output-dir path/to/output/
```

## Mid Traffic
```
python modify_traffic.py --dat path/to/file.dat --json path/to/file_V3.json --lower 0.73 --upper 0.87 --seed 42 --output-dir path/to/output/
```

## High Traffic
```
python modify_traffic.py --dat path/to/file.dat --json path/to/file_V3.json --lower 0.6 --upper 0.73 --seed 42 --output-dir path/to/output/
```