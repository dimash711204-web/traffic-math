import json

def parse_edge_list(text):
    """
    Parse text where each line: "u v [w]"  -> returns list of (u,v,w)
    """
    edges = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 2:
            u, v = parts
            w = 1
        else:
            u, v, w = parts[0], parts[1], parts[2]
            try:
                w = float(w)
            except:
                try:
                    w = int(w)
                except:
                    w = 1
        edges.append((u, v, w))
    return edges

def to_cytoscape(nodes, edges):
    elements = []
    for n in nodes:
        elements.append({"data": {"id": n, "label": str(n)}})
    for idx, (u, v, w) in enumerate(edges):
        elements.append({"data": {"id": f"e{idx}_{u}_{v}", "source": u, "target": v, "label": str(w)}})
    return elements

def edges_to_adj_list(edges, directed=False):
    adj = {}
    for u, v, w in edges:
        adj.setdefault(u, []).append({"v": v, "w": w})
        if not directed:
            adj.setdefault(v, []).append({"v": u, "w": w})
    return adj

def adj_list_to_edges(adj, directed=False):
    # adj is dict {u: [{"v":v,"w":w}, ...], ...} OR {u: ["v","v2"] }
    edges = []
    seen = set()
    for u, lst in adj.items():
        for it in lst:
            if isinstance(it, dict):
                v = it.get("v")
                w = it.get("w", 1)
            else:
                v = it
                w = 1
            key = (u, v, w)
            if not directed:
                key_rev = (v, u, w)
                if key_rev in seen:
                    continue
            edges.append(key)
            seen.add(key)
    return edges

def edges_to_adj_matrix(edges, directed=False):
    nodes = sorted({u for u,v,w in edges} | {v for u,v,w in edges})
    idx = {n:i for i,n in enumerate(nodes)}
    n = len(nodes)
    m = [[0]*n for _ in range(n)]
    for u, v, w in edges:
        i = idx[u]; j = idx[v]
        try:
            val = float(w)
        except:
            val = 1
        m[i][j] = val
        if not directed:
            m[j][i] = val
    return {"nodes": nodes, "matrix": m}

def matrix_to_edges(matrix, nodes, directed=False):
    edges = []
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val:
                u = nodes[i]; v = nodes[j]
                edges.append((u, v, val))
    if not directed:
        # optionally remove duplicate (keep i<j)
        filtered = []
        seen = set()
        for u,v,w in edges:
            if (v,u,w) in seen:
                continue
            filtered.append((u,v,w))
            seen.add((u,v,w))
        return filtered
    return edges