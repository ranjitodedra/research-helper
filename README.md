# Research Helper Tools

## countEdges

This modules take path from the GA and provides the number of edges which I can use as visits value in CPLEX.

just enenter path in UI or python program like this

```
D -> 2 -> C3 -> 7 -> C1 -> 4 -> BSS1 -> C5 -> 3 -> C6 -> BSS4 -> C7 -> C2 -> C4 -> C8 -> C9 -> 5 -> 1 -> D
```

## customer&bssLists

based on input, which we get from network generator we can generate here input for CPLEX, its the lists we need to provides before matrixs.

just provide 

```
idx2label = {
    0: "D",
    1: "1",
    2: "2",
    3: "BSS1",
    4: "C1",
    5: "C2",
    6: "3",
    7: "4",
    8: "5",
    9: "C3",
    10: "C4",
    11: "BSS2",
    12: "C5",
    13: "6",
    14: "BSS3",
    15: "C6",
    16: "7",
    17: "8",
    18: "C7",
    19: "C8",
    20: "C9",
    21: "BSS4",
}
```

and run the program

## ExampleTracker

This module is just storage for all examples I run

## InputGenerator

Takes input from Network Generator and generate final inputs for all the programs

## maintainRatio

just take total number of nodes and provide the number of customer and bss we should keep

## NetworkGenerator

generate network based on number of nodes provided

## visualization

To run

```
python visualize_graph.py graph.json
```