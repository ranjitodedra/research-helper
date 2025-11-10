# Research Helper Tools

## add_zero

There are three ways to give it matrices:

(a) One matrix

Paste a single matrix:
```
[
 [0, 1, 1],
 [1, 0, 1],
 [1, 1, 0]
]
```

Then press Enter (and Ctrl+D or Ctrl+Z + Enter on Windows).

→ Output:
```
[[0, 1, 1, 0], [1, 0, 1, 0], [1, 1, 0, 0]]
```

(b) Several matrices separated by ---

Paste:
```
[
 [0, 1, 1],
 [1, 0, 1]
]
---
[
 [1.1, 2.2],
 [3.3, 4.4]
]
```

Press Enter, then Ctrl+D (or Ctrl+Z + Enter).
It will print both modified matrices, separated again by ---.

(c) List of matrices in Python syntax

If you already have them in a list form:
```
[
 [
  [0,1],
  [1,0]
 ],
 [
  [4.5,2.2],
  [3.1,0.0]
 ]
]
```
It will output the same structure with each row extended by one 0.

## visualization

Basic Usage

1. Basic command (displays the graph):
```
python visualize_graph.py graph.json
```
2. Save to a file:
```
python visualize_graph.py graph.json -o output.png
```
3. View all options:
```
python visualize_graph.py --help
```