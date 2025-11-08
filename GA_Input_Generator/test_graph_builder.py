from input_generator_gnn import build_from_adjacency
import json

def normalize(g):
    g = json.loads(json.dumps(g))
    g["edges"].sort(key=lambda e: (e["from"], e["to"]))
    return g

def same_graph(g1, g2):
    return normalize(g1) == normalize(g2)

def run_tests():
    tests = []

    # Example 1 (10 customers)
    table1 = [
    [1, 2], #D
    [0, 2, 3, 11], #1
    [0, 1, 3, 14], #2
    [1, 2, 13], #3
    [10, 11, 12, 13], #4
    [13, 15, 14, 9], #5
    [12, 13, 15, 7], #6
    [12, 6, 8, 16], #7
    [15, 16, 7], #8
    [5], #9
    [11,12,4,21,22], #10
    [1,4,10,23], #11
    [10,4,6,7,24], #12
    [3,4,6,5,14], #13
    [2,13,5], #14
    [5,6,8,19], #15
    [7,8,20], #16
    [20,18], #17
    [19,17], #18
    [15,20,18], #19
    [16,17,19], #20
    [23,10], #21
    [24,10], #22
    [11,21], #23
    [12,22], #24
]


    idx2label1 = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 19:"19", 20:"20", 23:"23", 24:"24",
    9:"BSS1", 10:"BSS2",
    11:"C1", 12:"C2", 13:"C3", 14:"C4", 15:"C5", 16:"C6", 17:"C7",18:"C8",21:"C9",22:"C10"
}
    node_types1 = {
    "D":    {"type":"depot"},
    "1":    {"type":"intersection"},
    "2":    {"type":"intersection"},
    "3":    {"type":"intersection"},
    "4":    {"type":"intersection"},
    "5":    {"type":"intersection"},
    "6":    {"type":"intersection"},
    "7":    {"type":"intersection"},
    "8":    {"type":"intersection"},
    "19":   {"type":"intersection"},
    "20":   {"type":"intersection"},
    "23":   {"type":"intersection"},
    "24":   {"type":"intersection"},
    "BSS1": {"type":"bss"},
    "BSS2": {"type":"bss"},
    "C1":   {"type":"customer"},
    "C2":   {"type":"customer"},
    "C3":   {"type":"customer"},
    "C4":   {"type":"customer"},
    "C5":   {"type":"customer"},
    "C6":   {"type":"customer"},
    "C7":   {"type":"customer"},
    "C8":   {"type":"customer"},
    "C9":   {"type":"customer"},
    "C10":  {"type":"customer"},
}
    expected1 = {
        "nodes": {
    "D": { "type": "depot"},
    "C1": { "type": "customer"},
    "C2": { "type": "customer"},
    "C3": { "type": "customer"},
    "C4": { "type": "customer"},
    "C5": { "type": "customer"},
    "C6": { "type": "customer"},
    "C7": { "type": "customer"},
    "C8": { "type": "customer"},
    "C9": { "type": "customer"},
    "C10": { "type": "customer"},
    "BSS1": { "type": "bss"},
    "BSS2": { "type": "bss"},
    "1": { "type": "intersection"},
    "2": { "type": "intersection"},
    "3": { "type": "intersection"},
    "4": { "type": "intersection"},
    "5": { "type": "intersection"},
    "6": { "type": "intersection"},
    "7": { "type": "intersection"},
    "8": { "type": "intersection"},
    "19": { "type": "intersection"},
    "20": { "type": "intersection"},
    "23": { "type": "intersection"},
    "24": { "type": "intersection"}
  },
        "edges": [
    { "from": "D", "to": "1",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "D", "to": "2",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "1", "to": "2",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "3",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "2", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "3",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "3", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "4", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "BSS2","distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "5", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "BSS1","distance": 8.0, "traffic_factor": 1.0 },

    { "from": "6", "to": "7",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "7", "to": "8",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "8", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C9", "to": "BSS2","distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C10","to": "BSS2","distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C1", "to": "BSS2","distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "BSS2","distance": 8.0, "traffic_factor": 1.0 },

    { "from": "19","to": "20",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "19","to": "C8",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "20","to": "C7",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "23","to": "C9",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "23","to": "C1",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "24","to": "C10", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "24","to": "C2",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C3","to": "C4",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C5","to": "19",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C6","to": "20",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C7","to": "C8",  "distance": 8.0, "traffic_factor": 1.0 }
  ]
    }


    # Example 2 (6 customers)
    table2 = [
    [1, 2], #D
    [0, 2, 3, 11], #1
    [0, 1, 3, 14], #2
    [1, 2, 13], #3
    [10, 11, 12, 13], #4
    [9, 13, 14, 15], #5
    [12, 13, 15, 7], #6
    [12, 6, 8, 16], #7
    [15, 16, 7], #8
    [5], #9
    [11,12,4], #10
    [1,4,10], #11
    [10,4,6,7], #12
    [3,4,6,5,14], #13
    [2,13,5], #14
    [5,6,8], #15
    [7,8], #16
]

    idx2label2 = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8",
    9:"BSS1", 10:"BSS2",
    11:"C1", 12:"C2", 13:"C3", 14:"C4", 15:"C5", 16:"C6"
    }
    node_types2 = {
    "D":    {"type":"depot"},
    "1":    {"type":"intersection"},
    "2":    {"type":"intersection"},
    "3":    {"type":"intersection"},
    "4":    {"type":"intersection"},
    "5":    {"type":"intersection"},
    "6":    {"type":"intersection"},
    "7":    {"type":"intersection"},
    "8":    {"type":"intersection"},
    "BSS1": {"type":"bss"},
    "BSS2": {"type":"bss"},
    "C1":   {"type":"customer"},
    "C2":   {"type":"customer"},
    "C3":   {"type":"customer"},
    "C4":   {"type":"customer"},
    "C5":   {"type":"customer"},
    "C6":   {"type":"customer"},
}
    expected2 = {
        "nodes": { 
    "D": { "type": "depot"},
    "C1": { "type": "customer"},
    "C2": { "type": "customer"},
    "C3": { "type": "customer"},
    "C4": { "type": "customer"},
    "C5": { "type": "customer"},
    "C6": { "type": "customer"},
    "BSS1": { "type": "bss"},
    "BSS2": { "type": "bss"},
    "1": { "type": "intersection"},
    "2": { "type": "intersection"},
    "3": { "type": "intersection"},
    "4": { "type": "intersection"},
    "5": { "type": "intersection"},
    "6": { "type": "intersection"},
    "7": { "type": "intersection"},
    "8": { "type": "intersection"}
  },
  "edges": [
    { "from": "D", "to": "1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "D", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "BSS1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "7", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C1", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C3", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 }
  ]
}

    # Example 3 (8 customers)

    table3 = [
    [1, 2],  # Node 0
    [0, 2, 3, 11],  # Node 1
    [0, 1, 3, 14],  # Node 2
    [1, 2, 13],  # Node 3
    [10, 11, 12, 13],  # Node 4
    [9, 13, 14, 15],  # Node 5
    [7, 12, 13, 15],  # Node 6
    [6, 8, 12, 16],  # Node 7
    [7, 15, 16],  # Node 8
    [5],  # Node 9
    [4, 11, 12],  # Node 10
    [1, 4, 10],  # Node 11
    [4, 6, 7, 10],  # Node 12
    [3, 4, 5, 6, 14],  # Node 13
    [2, 5, 13],  # Node 14
    [5, 6, 8, 19],  # Node 15
    [7, 8, 20],  # Node 16
    [18, 20],  # Node 17
    [17, 19],  # Node 18
    [15, 18, 20],  # Node 19
    [16, 17, 19],  # Node 20
]

    idx2label3 = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8",19:"19", 20:"20",
    9:"BSS1", 10:"BSS2",
    11:"C1", 12:"C2", 13:"C3", 14:"C4", 15:"C5", 16:"C6", 17:"C7",18:"C8"
    }
    node_types3 = {
    "D":    {"type":"depot"},
    "1":    {"type":"intersection"},
    "2":    {"type":"intersection"},
    "3":    {"type":"intersection"},
    "4":    {"type":"intersection"},
    "5":    {"type":"intersection"},
    "6":    {"type":"intersection"},
    "7":    {"type":"intersection"},
    "8":    {"type":"intersection"},
    "19":   {"type":"intersection"},
    "20":   {"type":"intersection"},
    "BSS1": {"type":"bss"},
    "BSS2": {"type":"bss"},
    "C1":   {"type":"customer"},
    "C2":   {"type":"customer"},
    "C3":   {"type":"customer"},
    "C4":   {"type":"customer"},
    "C5":   {"type":"customer"},
    "C6":   {"type":"customer"},
    "C7":   {"type":"customer"},
    "C8":   {"type":"customer"},
}
    expected3 = {
        "nodes": { 
    "D": { "type": "depot"},
    "C1": { "type": "customer"},
    "C2": { "type": "customer"},
    "C3": { "type": "customer"},
    "C4": { "type": "customer"},
    "C5": { "type": "customer"},
    "C6": { "type": "customer"},
    "C7": { "type": "customer"},
    "C8": { "type": "customer"},
    "BSS1": { "type": "bss"},
    "BSS2": { "type": "bss"},
    "1": { "type": "intersection"},
    "2": { "type": "intersection"},
    "3": { "type": "intersection"},
    "4": { "type": "intersection"},
    "5": { "type": "intersection"},
    "6": { "type": "intersection"},
    "7": { "type": "intersection"},
    "8": { "type": "intersection"},
    "19": { "type": "intersection"},
    "20": { "type": "intersection"}
  },
   "edges": [
    { "from": "D", "to": "1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "D", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "BSS1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "7", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C5", "to": "19", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C1", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C3", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "19", "to": "20", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "19", "to": "C8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C7", "to": "C8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "20", "to": "C7", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C6", "to": "20", "distance": 8.0, "traffic_factor": 1.0 }
  ]
    }

    table4 = [
    [1, 2],  # Node 0
    [0, 2, 12, 13],  # Node 1
    [0, 1, 14],  # Node 2
    [14, 15, 17, 23],  # Node 3
    [12, 15, 16],  # Node 4
    [15, 16, 17],  # Node 5
    [16, 20],  # Node 6
    [17, 20],  # Node 7
    [16, 18],  # Node 8
    [19, 20],  # Node 9
    [20, 21, 24],  # Node 10
    [22, 23, 24],  # Node 11
    [1, 4, 25],  # Node 12
    [1, 14, 15],  # Node 13
    [2, 3, 13],  # Node 14
    [3, 4, 5, 13],  # Node 15
    [4, 5, 6, 8],  # Node 16
    [3, 5, 7],  # Node 17
    [8, 19],  # Node 18
    [9, 18],  # Node 19
    [6, 7, 9, 10],  # Node 20
    [10, 22],  # Node 21
    [11, 21],  # Node 22
    [3, 11],  # Node 23
    [10, 11],  # Node 24
    [12, 16],  # Node 25
]

    idx2label4 = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"11",
    24:"BSS1", 25:"BSS2",
    12:"C1", 13:"C2", 14:"C3", 15:"C4", 16:"C5", 17:"C6", 18:"C7",19:"C8",20:"C9",21:"C10",22:"C11",23:"C12" 
    }

    node_types4 = {
    "D":    {"type":"depot"},
    "1":    {"type":"intersection"},
    "2":    {"type":"intersection"},
    "3":    {"type":"intersection"},
    "4":    {"type":"intersection"},
    "5":    {"type":"intersection"},
    "6":    {"type":"intersection"},
    "7":    {"type":"intersection"},
    "8":    {"type":"intersection"},
    "9":    {"type":"intersection"},
    "10":   {"type":"intersection"},
    "11":   {"type":"intersection"},
    "BSS1": {"type":"bss"},
    "BSS2": {"type":"bss"},
    "C1":   {"type":"customer"},
    "C2":   {"type":"customer"},
    "C3":   {"type":"customer"},
    "C4":   {"type":"customer"},
    "C5":   {"type":"customer"},
    "C6":   {"type":"customer"},
    "C7":   {"type":"customer"},
    "C8":   {"type":"customer"},
    "C9":   {"type":"customer"},
    "C10":  {"type":"customer"},
    "C11":  {"type":"customer"},
    "C12":  {"type":"customer"},
}
    expected4 = {
        "nodes": {
    "D": { "type": "depot"},
    "C1": { "type": "customer"},
    "C2": { "type": "customer"},
    "C3": { "type": "customer"},
    "C4": { "type": "customer"},
    "C5": { "type": "customer"},
    "C6": { "type": "customer"},
    "C7": { "type": "customer"},
    "C8": { "type": "customer"},
    "C9": { "type": "customer"},
    "C10": { "type": "customer"},
    "C11": { "type": "customer"},
    "C12": { "type": "customer"},
    "BSS1": { "type": "bss"},
    "BSS2": { "type": "bss"},
    "1": { "type": "intersection"},
    "2": { "type": "intersection"},
    "3": { "type": "intersection"},
    "4": { "type": "intersection"},
    "5": { "type": "intersection"},
    "6": { "type": "intersection"},
    "7": { "type": "intersection"},
    "8": { "type": "intersection"},
    "9": { "type": "intersection"},
    "10": { "type": "intersection"},
    "11": { "type": "intersection"}
  },
  "edges": [
    { "from": "D", "to": "1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "D", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "3", "to": "C12", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C9", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C9", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C6", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "BSS2", "to": "C5", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "9", "to": "C8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "9", "to": "C9", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C7", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "10", "to": "C10", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "10", "to": "C9", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "10", "to": "BSS1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "11", "to": "C11", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "11", "to": "BSS1", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "11", "to": "C12", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C1", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "C4", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "C3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C7", "to": "C8", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C10", "to": "C11", "distance": 8.0, "traffic_factor": 1.0 }
  ]
    }

    table5 = [
    [1, 2],  # Node 0
    [0, 2, 3, 11],  # Node 1
    [0, 1, 3, 14],  # Node 2
    [1, 2, 13],  # Node 3
    [10, 11, 12, 13],  # Node 4
    [9, 13, 14, 15],  # Node 5
    [7, 12, 13, 15],  # Node 6
    [6, 8, 12, 16, 25, 26],  # Node 7
    [7, 15, 16],  # Node 8
    [5],  # Node 9
    [4, 11, 12, 21, 22],  # Node 10
    [1, 4, 10, 23],  # Node 11
    [4, 6, 7, 10, 24],  # Node 12
    [3, 4, 5, 6, 14],  # Node 13
    [2, 5, 13],  # Node 14
    [5, 6, 8, 19],  # Node 15
    [7, 8, 20],  # Node 16
    [18, 20],  # Node 17
    [17, 19],  # Node 18
    [15, 18, 20],  # Node 19
    [16, 17, 19, 25, 27],  # Node 20
    [10, 23],  # Node 21
    [10, 24],  # Node 22
    [11, 21],  # Node 23
    [12, 22],  # Node 24
    [7, 20, 28],  # Node 25
    [7, 30],  # Node 26
    [20, 31],  # Node 27
    [25, 31, 32, 30],  # Node 28
    [30, 32],  # Node 29
    [26, 28, 29],  # Node 30
    [27, 28, 32],  # Node 31
    [29, 28, 31],  # Node 32
]

    idx2label5 = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 19:"19", 20:"20", 23:"23", 24:"24", 30:"30", 31:"31", 32:"32",
    9:"BSS1", 10:"BSS2", 25:"BSS3",
    11:"C1", 12:"C2", 13:"C3", 14:"C4", 15:"C5", 16:"C6", 17:"C7",18:"C8",21:"C9",22:"C10",26:"C11",27:"C12",28:"C13",29:"C14"
    }

    node_types5 = {
    "D":    {"type":"depot"},
    "1":    {"type":"intersection"},
    "2":    {"type":"intersection"},
    "3":    {"type":"intersection"},
    "4":    {"type":"intersection"},
    "5":    {"type":"intersection"},
    "6":    {"type":"intersection"},
    "7":    {"type":"intersection"},
    "8":    {"type":"intersection"},
    "19":   {"type":"intersection"},
    "20":   {"type":"intersection"},
    "23":   {"type":"intersection"},
    "24":   {"type":"intersection"},
    "30":   {"type":"intersection"},
    "31":   {"type":"intersection"},
    "32":   {"type":"intersection"},
    "BSS1": {"type":"bss"},
    "BSS2": {"type":"bss"},
    "BSS3": {"type":"bss"},
    "C1":   {"type":"customer"},
    "C2":   {"type":"customer"},
    "C3":   {"type":"customer"},
    "C4":   {"type":"customer"},
    "C5":   {"type":"customer"},
    "C6":   {"type":"customer"},
    "C7":   {"type":"customer"},
    "C8":   {"type":"customer"},
    "C9":   {"type":"customer"},
    "C10":  {"type":"customer"},
    "C11":  {"type":"customer"},
    "C12":  {"type":"customer"},
    "C13":  {"type":"customer"},
    "C14":  {"type":"customer"},
}

    expected5 = {

        "nodes": {
    "D": { "type": "depot"},
    "C1": { "type": "customer"},
    "C2": { "type": "customer"},
    "C3": { "type": "customer"},
    "C4": { "type": "customer"},
    "C5": { "type": "customer"},
    "C6": { "type": "customer"},
    "C7": { "type": "customer"},
    "C8": { "type": "customer"},
    "C9": { "type": "customer"},
    "C10": { "type": "customer"},
    "C11": { "type": "customer"},
    "C12": { "type": "customer"},
    "C13": { "type": "customer"},
    "C14": { "type": "customer"},
    "BSS1": { "type": "bss"},
    "BSS2": { "type": "bss"},
    "BSS3": { "type": "bss"},
    "1": { "type": "intersection"},
    "2": { "type": "intersection"},
    "3": { "type": "intersection"},
    "4": { "type": "intersection"},
    "5": { "type": "intersection"},
    "6": { "type": "intersection"},
    "7": { "type": "intersection"},
    "8": { "type": "intersection"},
    "19": { "type": "intersection"},
    "20": { "type": "intersection"},
    "23": { "type": "intersection"},
    "24": { "type": "intersection"},
    "30": { "type": "intersection"},
    "31": { "type": "intersection"},
    "32": { "type": "intersection"}
  },
    "edges": [
    { "from": "D", "to": "1",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "D", "to": "2",   "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "1", "to": "2",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "3",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "1", "to": "C1",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "2", "to": "3",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "2", "to": "C4",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "3", "to": "C3",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "4", "to": "C1",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C2",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "4", "to": "C3",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "5", "to": "C5",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C3",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "C4",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "5", "to": "BSS1", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "6", "to": "7",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C3",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C2",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "6", "to": "C5",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "7", "to": "8",   "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C6",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "C2",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "8", "to": "C6",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "8", "to": "C5",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C9", "to": "BSS2",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C10", "to": "BSS2", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C1", "to": "BSS2",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C2", "to": "BSS2",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "19", "to": "20",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "19", "to": "C8",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "20", "to": "C7",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "23", "to": "C9",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "23", "to": "C1",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "24", "to": "C10", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "24", "to": "C2",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C3", "to": "C4",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C5", "to": "19",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C6", "to": "20",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C7", "to": "C8",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "7", "to": "C11",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "20","to": "C12",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "20","to": "BSS3", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "7", "to": "BSS3",  "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C14","to": "32",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C13","to": "BSS3", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C13", "to": "31", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C13", "to": "32", "distance": 8.0, "traffic_factor": 1.0 },

    { "from": "C12", "to": "31", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "31", "to": "32", "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C11","to": "30",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C13","to": "30",  "distance": 8.0, "traffic_factor": 1.0 },
    { "from": "C14","to": "30",  "distance": 8.0, "traffic_factor": 1.0 }

  ]

    }

    tests.append((table1, idx2label1, node_types1, expected1))
    tests.append((table2, idx2label2, node_types2, expected2))
    tests.append((table3, idx2label3, node_types3, expected3))
    tests.append((table4, idx2label4, node_types4, expected4))
    tests.append((table5, idx2label5, node_types5, expected5))


    # === Add more examples below ===
    # Copy the pattern above for 4 more cases
    # (table2, idx2label2, node_types2, expected2), etc.


    
    # -------------------- RUN --------------------
    passed = 0
    for i, (table, idx2label, node_types, expected) in enumerate(tests, 1):
        result = build_from_adjacency(table, idx2label, node_types)
        ok = same_graph(result, expected)
        print(f"Test {i}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print("Expected:\n", json.dumps(expected, indent=2))
            print("Got:\n", json.dumps(result, indent=2))
        print("-"*50)
        if ok: passed += 1

    print(f"\nSummary: {passed}/{len(tests)} passed.")

if __name__ == "__main__":
    run_tests()
