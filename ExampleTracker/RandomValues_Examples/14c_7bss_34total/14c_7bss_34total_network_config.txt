======================================================================
NETWORK CONFIGURATION
======================================================================

Total Nodes: 34
Customers: 14
BSS Stations: 7
Intersections: 12
Depot: 1

======================================================================

table = [
    [1, 2],  # Node 0: D (depot)
    [0, 2, 9, 14],  # Node 1: 1 (intersection)
    [0, 1, 20, 22, 24],  # Node 2: 2 (intersection)
    [12, 23, 26, 32],  # Node 3: C1 (customer)
    [6, 13, 19],  # Node 4: BSS1 (bss)
    [12, 18, 23, 25, 29],  # Node 5: C2 (customer)
    [4, 9, 15, 16, 25],  # Node 6: C3 (customer)
    [28, 30],  # Node 7: 3 (intersection)
    [10, 11, 17, 19],  # Node 8: 4 (intersection)
    [1, 6, 15, 16],  # Node 9: C4 (customer)
    [8, 21, 22],  # Node 10: C5 (customer)
    [8, 17, 28, 30, 32],  # Node 11: 5 (intersection)
    [3, 5, 23, 25],  # Node 12: 6 (intersection)
    [4, 17, 19],  # Node 13: C6 (customer)
    [1, 15, 16, 31],  # Node 14: BSS2 (bss)
    [6, 9, 14, 31],  # Node 15: C7 (customer)
    [6, 9, 14],  # Node 16: C8 (customer)
    [8, 11, 13, 19, 30],  # Node 17: C9 (customer)
    [5, 23, 25, 29],  # Node 18: BSS3 (bss)
    [4, 8, 13, 17],  # Node 19: BSS4 (bss)
    [2, 21, 22, 24],  # Node 20: BSS5 (bss)
    [10, 20, 22],  # Node 21: 7 (intersection)
    [2, 10, 20, 21, 24],  # Node 22: 8 (intersection)
    [3, 5, 12, 18, 29],  # Node 23: BSS6 (bss)
    [2, 20, 22],  # Node 24: 9 (intersection)
    [5, 6, 12, 18, 29],  # Node 25: C10 (customer)
    [3, 27, 32, 33],  # Node 26: C11 (customer)
    [26, 28, 30, 32, 33],  # Node 27: C12 (customer)
    [7, 11, 27, 30],  # Node 28: 10 (intersection)
    [5, 18, 23, 25],  # Node 29: 11 (intersection)
    [7, 11, 17, 27, 28],  # Node 30: BSS7 (bss)
    [14, 15],  # Node 31: C13 (customer)
    [3, 11, 26, 27, 33],  # Node 32: 12 (intersection)
    [26, 27, 32],  # Node 33: C14 (customer)
]

idx2label = {
    0: "D",
    1: "1",
    2: "2",
    3: "C1",
    4: "BSS1",
    5: "C2",
    6: "C3",
    7: "3",
    8: "4",
    9: "C4",
    10: "C5",
    11: "5",
    12: "6",
    13: "C6",
    14: "BSS2",
    15: "C7",
    16: "C8",
    17: "C9",
    18: "BSS3",
    19: "BSS4",
    20: "BSS5",
    21: "7",
    22: "8",
    23: "BSS6",
    24: "9",
    25: "C10",
    26: "C11",
    27: "C12",
    28: "10",
    29: "11",
    30: "BSS7",
    31: "C13",
    32: "12",
    33: "C14",
}

node_types = {
    "BSS1": "bss",
    "BSS2": "bss",
    "BSS3": "bss",
    "BSS4": "bss",
    "BSS5": "bss",
    "BSS6": "bss",
    "BSS7": "bss",
    "C1": "customer",
    "C10": "customer",
    "C11": "customer",
    "C12": "customer",
    "C13": "customer",
    "C14": "customer",
    "C2": "customer",
    "C3": "customer",
    "C4": "customer",
    "C5": "customer",
    "C6": "customer",
    "C7": "customer",
    "C8": "customer",
    "C9": "customer",
    "D": "depot",
    "1": "intersection",
    "10": "intersection",
    "11": "intersection",
    "12": "intersection",
    "2": "intersection",
    "3": "intersection",
    "4": "intersection",
    "5": "intersection",
    "6": "intersection",
    "7": "intersection",
    "8": "intersection",
    "9": "intersection",
}
