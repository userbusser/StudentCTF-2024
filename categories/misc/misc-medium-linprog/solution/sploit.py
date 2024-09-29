import numpy as np
from scipy.optimize import linprog, milp, Bounds
from scipy.optimize import LinearConstraint
import re
from pwn import remote


class Solver_lin_prog():
    def __init__(self) -> None:
        pass

    def solve_knapsack_task(self, values, sizes, C):
        constraints = LinearConstraint(A=sizes, lb=0, ub=C)
        bounds = Bounds(0, 1)
        res = milp(c=values, constraints=constraints,
                   integrality=True, bounds=bounds)
        if res.success:
            result_vector = res.x.tolist()
            result_vector = [int(i) for i in result_vector]
            return [result_vector, int(res.fun)]
        else:
            return [None, None]

    def solve_transport_task(self, lanes, carriers, cost, demand, capacity):
        cost = np.array(cost)
        A_eq = np.zeros(lanes*carriers*lanes).reshape(lanes, lanes*carriers)
        for l in range(lanes):
            for var in range(l*carriers, l*carriers+carriers):
                A_eq[l, var] = 1
        A_ub = np.zeros(carriers*lanes*carriers).reshape(carriers, lanes*carriers)
        for c in range(carriers):
            for var in range(c, lanes*carriers, carriers):
                A_ub[c, var] = 1
        res = linprog(cost.flatten(), A_eq=A_eq, b_eq=demand, 
                      A_ub=A_ub, b_ub=capacity)
        if res.success:
            result_vector = res.x.tolist()
            result_matrix = []
            a = []
            for i in range(len(result_vector)):
                a.append(int(result_vector[i]))
                if i != 0 and (i+1) % carriers == 0:
                    result_matrix.append(a)
                    a = []
            return [result_matrix, int(res.fun)]
        else:
            return [None, None]

    def solve_classic_and_int_task_lin_prog(self, Q, A_ub, b_ub, A_eq, b_eq, integrality=False):
        try:
            if len(A_ub) == 0:
                solve = linprog(Q, A_eq=A_eq, b_eq=b_eq, integrality=integrality)
            elif len(A_eq) == 0:
                solve = linprog(Q, A_ub, b_ub, integrality=integrality)
            else:
                solve = linprog(Q, A_ub, b_ub, A_eq, b_eq, integrality=integrality)
            if solve.success:
                result_vector = solve.x.tolist()
                result_vector = [round(i, 2) for i in result_vector]
                return [result_vector, round(solve.fun, 2)]
            else:
                return [None, None]
        except Exception as e:
            # print(e)
            return [None, None]


def parser_task_and_solver(r: remote, task: str, integrality: bool = False):
    solver = Solver_lin_prog()
    regular_coef_xi = r"\(([0-9.-]+)\)\*x"
    vector_xi, answer_task = [], []
    if task == "knapsack":
        ans = r.recvline().strip().decode()
        sizes = list(map(int, re.findall(regular_coef_xi, ans)))
        C = ans.split(" <= ")[1]
        r.recvline()
        ans = r.recvline().strip().decode()
        values = list(map(int, re.findall(regular_coef_xi, ans)))
        if "max" in ans:
            values = [-i for i in values]
        vector_xi, answer_task = solver.solve_knapsack_task(values, sizes, C)
        if "max" in ans:
            answer_task *= -1

    elif task == "transport":
        ans = r.recvline().strip().decode()
        demand = eval(ans.split(": ")[1])
        lanes = len(demand)
        ans = r.recvline().strip().decode()
        capacity = eval(ans.split(": ")[1])
        carriers = len(capacity)
        cost = []
        r.recvline()
        for _ in range(lanes):
            ans = r.recvline().strip().decode()[1:-1]
            cost.append(list(map(int, ans.split())))
        vector_xi, answer_task = solver.solve_transport_task(lanes, carriers, cost, demand, capacity)
    else:
        if integrality:
            ans = r.recvuntil(b"Find an integer solution: ").decode()
        else:
            ans = r.recvuntil(b"Find solution: ").decode()
        array_of_conditions = ans.split("\n")
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for i in range(len(array_of_conditions)-2):
            coef_xi = list(map(float, re.findall(regular_coef_xi, array_of_conditions[i])))
            if "<=" in array_of_conditions[i]:
                A_ub.append(coef_xi)
                b_ub.append(float(array_of_conditions[i].split(" <= ")[1]))
            elif ">=" in array_of_conditions[i]:
                coef_xi = [-k for k in coef_xi]
                A_ub.append(coef_xi)
                b_ub.append(-1 * (float(array_of_conditions[i].split(" >= ")[1])))
            elif "==" in array_of_conditions[i]:
                A_eq.append(coef_xi)
                b_eq.append(float(array_of_conditions[i].split(" == ")[1]))
        ans = r.recvline().strip().decode()
        Q = list(map(float, re.findall(regular_coef_xi, ans)))
        if "max" in ans:
            Q = [-k for k in Q]
        vector_xi, answer_task = solver.solve_classic_and_int_task_lin_prog(Q, A_ub, b_ub, A_eq, b_eq, integrality)
        if "max" in ans:
            answer_task *= -1
    return vector_xi, answer_task


r = remote("85.143.206.150", 13338)

for i in range(16):
    print(r.recvuntil(f"Problem {i+1}/16:\n".encode()))
    integrality = False
    ans = r.recvline()
    task = ""
    if b"Wait" in ans:
        integrality = True

    ans = r.recvline()
    if b"xi = 0 or 1, for anyone i" in ans:
        task = "knapsack"
    elif b"warehouses from which it is necessary to distribute" in ans:
        task = "transport"
    else:
        task = "linprog"
    vector_xi, answer_task = parser_task_and_solver(r, task, integrality)
    print(vector_xi, answer_task)
    r.recvuntil(b": ")
    r.sendline(str(vector_xi).encode())
    r.recvuntil(b": ")
    r.sendline(str(answer_task).encode())

r.interactive()
    