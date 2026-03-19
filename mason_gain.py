# -*- coding: utf-8 -*-
"""
Mason 增益公式（符号版）

本实现输出三类核心结果（字典形式）：
1) 前向通路字典
2) 单回路字典
3) 互不接触回路组合字典

并输出字符串公式：
- Δ 公式
- 每条前向通路对应的 Δk 公式
- 总传递函数 T 的标签公式与展开公式
"""


class SignalFlowGraph:
    """信号流图 + Mason 公式（字符串表达）求解器。"""

    def __init__(self):
        self._edges = {}
        self._adj = {}
        self._next_eid = 0

    def add_edge(self, src, dst, gain):
        """添加一条有向边，gain 建议传字符串符号，如 'G1'。"""
        eid = self._next_eid
        self._next_eid += 1

        edge = {"eid": eid, "src": src, "dst": dst, "gain": str(gain)}
        self._edges[eid] = edge

        if src not in self._adj:
            self._adj[src] = []
        if dst not in self._adj:
            self._adj[dst] = []

        self._adj[src].append(eid)
        return eid

    def _mul_expr(self, factors):
        """把多个因子拼成乘积字符串。"""
        factors = [f for f in factors if f and f != "1"]
        if not factors:
            return "1"
        if len(factors) == 1:
            return factors[0]
        return "(" + "*".join(factors) + ")"

    def _sum_expr(self, terms):
        """把多个项拼成加法字符串。"""
        terms = [t for t in terms if t]
        if not terms:
            return "0"
        if len(terms) == 1:
            return terms[0]
        return "(" + " + ".join(terms) + ")"

    def _gain_expr_of_edges(self, edge_ids):
        factors = []
        for eid in edge_ids:
            factors.append(self._edges[eid]["gain"])
        return self._mul_expr(factors)

    def find_forward_paths(self, source, sink):
        """DFS 枚举所有简单前向通路。"""
        if source not in self._adj or sink not in self._adj:
            return []

        paths = []

        def dfs(curr, visited_nodes, edge_trace):
            if curr == sink:
                paths.append(
                    {
                        "edge_ids": tuple(edge_trace), "node_set": set(visited_nodes),
                        "gain_expr": self._gain_expr_of_edges(tuple(edge_trace)),
                    }
                )
                return

            for eid in self._adj[curr]:
                nxt = self._edges[eid]["dst"]
                if nxt in visited_nodes:
                    continue
                visited_nodes.add(nxt)
                edge_trace.append(eid)
                dfs(nxt, visited_nodes, edge_trace)
                edge_trace.pop()
                visited_nodes.remove(nxt)

        dfs(source, {source}, [])
        return paths

    def _tarjan_scc(self, nodes_subset):
        """Tarjan 算法求 SCC。"""
        nodes_subset = set(nodes_subset)
        index = 0
        index_map = {}
        low = {}
        stack = []
        on_stack = set()
        sccs = []

        def strongconnect(v):
            nonlocal index
            index_map[v] = index
            low[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)

            for eid in self._adj.get(v, []):
                w = self._edges[eid]["dst"]
                if w not in nodes_subset:
                    continue
                if w not in index_map:
                    strongconnect(w)
                    low[v] = min(low[v], low[w])
                elif w in on_stack:
                    low[v] = min(low[v], index_map[w])

            if low[v] == index_map[v]:
                comp = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    comp.add(w)
                    if w == v:
                        break
                sccs.append(comp)

        for v in nodes_subset:
            if v not in index_map:
                strongconnect(v)

        return sccs

    def _has_cycle_in_scc(self, scc):
        if len(scc) > 1:
            return True
        v = next(iter(scc))
        for eid in self._adj.get(v, []):
            if self._edges[eid]["dst"] == v:
                return True
        return False

    def find_loops(self):
        """Johnson + SCC 枚举所有简单回路。"""
        all_nodes = list(self._adj.keys())
        node_rank = {node: i for i, node in enumerate(all_nodes)}
        loops = []

        start_idx = 0
        while start_idx < len(all_nodes):
            candidate_nodes = set(all_nodes[start_idx:])
            sccs = self._tarjan_scc(candidate_nodes)
            cyclic_sccs = [comp for comp in sccs if self._has_cycle_in_scc(comp)]
            if not cyclic_sccs:
                break

            chosen_scc = min(cyclic_sccs, key=lambda c: min(node_rank[x] for x in c))
            s = min(chosen_scc, key=lambda x: node_rank[x])

            adj_in_scc = {}
            for v in chosen_scc:
                adj_in_scc[v] = []
                for eid in self._adj.get(v, []):
                    w = self._edges[eid]["dst"]
                    if w in chosen_scc:
                        adj_in_scc[v].append(eid)

            blocked = set()
            block_map = {v: set() for v in chosen_scc}
            edge_stack = []

            def unblock(u):
                if u in blocked:
                    blocked.remove(u)
                    while block_map[u]:
                        w = block_map[u].pop()
                        unblock(w)

            def circuit(v):
                found_cycle = False
                blocked.add(v)

                for eid in adj_in_scc.get(v, []):
                    w = self._edges[eid]["dst"]
                    if w == s:
                        cycle_edge_ids = tuple(edge_stack + [eid])
                        node_set = set()
                        for ceid in cycle_edge_ids:
                            node_set.add(self._edges[ceid]["src"])
                            node_set.add(self._edges[ceid]["dst"])

                        loops.append(
                            {
                                "edge_ids": cycle_edge_ids, "node_set": node_set,
                                "gain_expr": self._gain_expr_of_edges(cycle_edge_ids),
                            }
                        )
                        found_cycle = True
                    elif w not in blocked:
                        edge_stack.append(eid)
                        if circuit(w):
                            found_cycle = True
                        edge_stack.pop()

                if found_cycle:
                    unblock(v)
                else:
                    for eid in adj_in_scc.get(v, []):
                        w = self._edges[eid]["dst"]
                        if v not in block_map[w]:
                            block_map[w].add(v)

                return found_cycle

            circuit(s)
            start_idx = node_rank[s] + 1

        return loops

    def _non_touching_loop_combos(self, loops):
        """枚举互不接触回路组合，返回按组合阶数分组的索引列表。"""
        grouped = {}

        def backtrack(start, used_nodes, picked):
            for i in range(start, len(loops)):
                if loops[i]["node_set"] & used_nodes:
                    continue

                next_picked = picked + [i]
                r = len(next_picked)
                if r >= 2:
                    grouped.setdefault(r, []).append(tuple(next_picked))

                backtrack(i + 1, used_nodes | loops[i]["node_set"], next_picked)

        backtrack(0, set(), [])
        return grouped

    def _build_delta_expr(self, loops):
        """根据给定回路集合构造 Δ 字符串，并返回明细。"""
        detail = {}
        if not loops:
            return "1", detail, {}

        sum1 = self._sum_expr([loop["gain_expr"] for loop in loops])
        detail[1] = sum1

        combos_grouped = self._non_touching_loop_combos(loops)
        combo_exprs = {}

        delta_parts = ["1", f"- {sum1}"]

        for r in sorted(combos_grouped.keys()):
            combo_terms = []
            for idxs in combos_grouped[r]:
                gain_prod = self._mul_expr([loops[i]["gain_expr"] for i in idxs])
                combo_terms.append(gain_prod)
            grouped_sum_expr = self._sum_expr(combo_terms)
            detail[r] = grouped_sum_expr
            combo_exprs[r] = combo_terms

            sign = "+" if r % 2 == 0 else "-"
            delta_parts.append(f"{sign} {grouped_sum_expr}")

        delta_expr = " ".join(delta_parts)
        return delta_expr, detail, combo_exprs

    def mason_gain(self, source, sink):
        """返回 Mason 求解结果（以字符串表达式为主）。"""
        forward_paths = self.find_forward_paths(source, sink)
        loops = self.find_loops()

        # 1) 前向通路字典
        forward_dict = {}
        for i, p in enumerate(forward_paths, start=1):
            forward_dict[f"P{i}"] = {
                "edge_ids": p["edge_ids"],
                "node_set": sorted(p["node_set"]),
                "gain_expr": p["gain_expr"],
            }

        # 2) 单回路字典
        loop_dict = {}
        for i, l in enumerate(loops, start=1):
            loop_dict[f"L{i}"] = {
                "edge_ids": l["edge_ids"],
                "node_set": sorted(l["node_set"]),
                "gain_expr": l["gain_expr"],
            }

        # 3) 互不接触回路组合字典（按阶数分组）
        non_touching_dict = {}
        all_combo_idx = self._non_touching_loop_combos(loops)
        loop_labels = [f"L{i}" for i in range(1, len(loops) + 1)]

        for r in sorted(all_combo_idx.keys()):
            non_touching_dict[f"{r}阶"] = {}
            for j, idxs in enumerate(all_combo_idx[r], start=1):
                combo_label = f"N{r}_{j}"
                involved = [loop_labels[idx] for idx in idxs]
                gain_expr = self._mul_expr([loops[idx]["gain_expr"] for idx in idxs])
                non_touching_dict[f"{r}阶"][combo_label] = {
                    "loops": involved, "gain_expr": gain_expr,
                }

        # Δ
        delta_expr, delta_detail, _ = self._build_delta_expr(loops)
        delta_formula = "Δ = " + delta_expr

        # Δk 与分子
        delta_k_formulas = {}
        numerator_terms = []
        numerator_label_terms = []

        for k, p in enumerate(forward_paths, start=1):
            non_touching_loops = []
            for l in loops:
                if not (l["node_set"] & p["node_set"]):
                    non_touching_loops.append(l)

            delta_k_expr, _, _ = self._build_delta_expr(non_touching_loops)
            delta_k_formulas[f"Δ{k}"] = delta_k_expr

            numerator_label_terms.append(f"P{k}*Δ{k}")
            numerator_terms.append(self._mul_expr([p["gain_expr"], delta_k_expr]))

        if not forward_paths:
            final_formula_label = "T = 0"
            final_formula_expanded = "T = 0"
        else:
            numerator_label = self._sum_expr(numerator_label_terms)
            numerator_expanded = self._sum_expr(numerator_terms)
            final_formula_label = f"T = {numerator_label} / Δ"
            final_formula_expanded = f"T = {numerator_expanded} / ({delta_expr})"

        return {
            "forward_paths": forward_dict,
            "loops": loop_dict,
            "non_touching_loops": non_touching_dict,
            "delta_formula": delta_formula,
            "delta_k_formulas": delta_k_formulas,
            "final_formula_label": final_formula_label,
            "final_formula_expanded": final_formula_expanded,
        }


def demo():
    """示例：全部使用字符串增益符号。"""
    g = SignalFlowGraph()

    g.add_edge("R", "X1", "G1")
    g.add_edge("X1", "X2", "G2")
    g.add_edge("X1", "X3", "G3")
    g.add_edge("X1", "X4", "G4")
    g.add_edge("X2", "X1", "H1")
    g.add_edge("X2", "X3", "G5")
    g.add_edge("X3", "X2", "H2")
    g.add_edge("X3", "X3", "G6")
    g.add_edge("X3", "X4", "G7")
    g.add_edge("X4", "X2", "H3")
    g.add_edge("X4", "C", "G8")

    result = g.mason_gain("R", "C")

    print("1) 前向通路字典:")
    for k, v in result["forward_paths"].items():
        print(k, v)

    print("\n2) 单回路字典:")
    for k, v in result["loops"].items():
        print(k, v)

    print("\n3) 互不接触回路组合字典:")
    for order_key, combos in result["non_touching_loops"].items():
        print(order_key, combos)

    print("\nΔ 公式:")
    print(result["delta_formula"])

    print("\nΔk 公式:")
    for k, v in result["delta_k_formulas"].items():
        print(f"{k} = {v}")

    print("\n总传递函数（标签式）:")
    print(result["final_formula_label"])

    print("\n总传递函数（展开式）:")
    print(result["final_formula_expanded"])


if __name__ == "__main__":
    demo()
