import gurobipy as gp
from gurobipy import GRB

n = 8
d = 4

# Uniform example: each node sends equally to every other node.
T_uniform = [[0 if s == t else d / (n - 1) for t in range(n)] for s in range(n)]

# Nonuniform example: every row and column sums to 4, with no self-traffic.
T_nonuniform = [
    [0,   2,   1.5, 0.5, 0,   0,   0,   0],
    [0,   0,   2,   1.5, 0.5, 0,   0,   0],
    [0,   0,   0,   2,   1.5, 0.5, 0,   0],
    [0,   0,   0,   0,   2,   1.5, 0.5, 0],
    [0,   0,   0,   0,   0,   2,   1.5, 0.5],
    [0.5, 0,   0,   0,   0,   0,   2,   1.5],
    [1.5, 0.5, 0,   0,   0,   0,   0,   2],
    [2,   1.5, 0.5, 0,   0,   0,   0,   0],
]

# Sparse example: each node sends 4 units only to the next node in a cycle.
T_sparse = [[d if t == (s + 1) % n else 0 for t in range(n)] for s in range(n)]

# Choose T_uniform, T_nonuniform, or T_sparse here.
T = T_sparse

print("Traffic matrix T (rows = sources, columns = destinations):")
for row in T:
    print(" ".join(f"{value:7.3f}" for value in row))

K = [(s, t) for s in range(n) for t in range(n) if s != t and T[s][t] > 0]

if not K:
    print("No traffic needs routing; lambda is unbounded.")
    raise SystemExit

model = gp.Model("network_design")

# 1. Topology variables
x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

# 2. Flow variables
f = model.addVars(
    K, range(n), range(n),
    lb=0,
    name="flow"
)

# 3. Concurrent flow factor
lam = model.addVar(lb=0, name="lambda")

# 4. Objective
model.setObjective(lam, GRB.MAXIMIZE)

# 5. Add topology constraints
for i in range(n):
    model.addConstr(gp.quicksum(x[i, j] for j in range(n)) == d)
    model.addConstr(gp.quicksum(x[j, i] for j in range(n)) == d)
    model.addConstr(x[i, i] == 0)

# 6. Add link capacity constraints
for i in range(n):
    for j in range(n):
        if i != j:
            model.addConstr(gp.quicksum(f[s, t, i, j] for s, t in K) <= x[i, j])

for s, t in K:
    for i in range(n):
        model.addConstr(f[s, t, i, i] == 0)

# 7. Add flow conservation constraints
for s, t in K:
    for v in range(n):
        outgoing = gp.quicksum(f[s, t, v, j] for j in range(n))
        incoming = gp.quicksum(f[s, t, i, v] for i in range(n))
        if v == s:
            model.addConstr(outgoing - incoming == lam * T[s][t])
        elif v == t:
            model.addConstr(outgoing - incoming == -lam * T[s][t])
        else:
            model.addConstr(outgoing - incoming == 0)

# 8. Optimize
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Optimal lambda:", lam.X)
    print("Installed links (0-based):")
    for i in range(n):
        for j in range(n):
            if x[i, j].X > 0.5:
                print(i, "->", j)
else:
    print("Optimization ended with status:", model.Status)
