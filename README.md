# CS 422 Assignment 4: Maximum Concurrent Flow and Network Design

The report for both parts is `report.tex` (built PDF: `report.pdf`, the single PDF for Brightspace). To build it, run `tectonic report.tex` in this folder.

## Part 1: Uniform traffic matrix

Part 1 is analytical: the construction, the upper bound and the optimality argument are all in Section 1 of the report, with no code.

## Part 2: Arbitrary (hose) traffic matrix

[gurobi.py](gurobi.py) uses a mixed-integer linear program to jointly choose a directed topology and route a given hose-model traffic matrix, maximizing the concurrent flow factor. The network has 8 nodes, each with exactly 4 incoming and 4 outgoing links of capacity 1, with no self-links or parallel links.

Choose an example by setting `T` to `T_uniform`, `T_nonuniform`, or `T_sparse` in the script. With `gurobipy` installed and a valid Gurobi license configured, run `python3 gurobi.py`. The script prints the traffic matrix and, when solved to optimality, the optimal flow factor and installed links.
