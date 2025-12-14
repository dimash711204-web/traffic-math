import streamlit as st
import json
import heapq

st.set_page_config(page_title="Quản lý giao thông – Logistics")

st.title("Ứng dụng quản lý giao thông – Logistics")
st.write("Môn: Cấu trúc rời rạc")

def parse_edge_list(text):
    adj = {}
    lines = text.strip().splitlines()

    for line in lines:
        u, v, w = line.split()
        w = int(w)

        if u not in adj:
            adj[u] = []
        if v not in adj:
            adj[v] = []

        adj[u].append({"v": v, "w": w})
        adj[v].append({"v": u, "w": w})  # đồ thị vô hướng

    return adj

# =======================
# Thuật toán
# =======================

def bfs(adj, start):
    visited = set()
    q = [start]
    order = []

    while q:
        u = q.pop(0)
        if u not in visited:
            visited.add(u)
            order.append(u)
            for e in adj[u]:
                if e["v"] not in visited:
                    q.append(e["v"])
    return order


def dfs(adj, start):
    visited = set()
    order = []

    def dfs_visit(u):
        visited.add(u)
        order.append(u)
        for e in adj[u]:
            if e["v"] not in visited:
                dfs_visit(e["v"])

    dfs_visit(start)
    return order


def dijkstra(adj, start):
    if start not in adj:
        raise ValueError(f"Đỉnh {start} không tồn tại trong đồ thị")

    dist = {v: float("inf") for v in adj}
    dist[start] = 0
    pq = [(0, start)]

    # Debug: In ra thông tin ban đầu
    print(f"Start Dijkstra from: {start}")

    while pq:
        d, u = heapq.heappop(pq)
        # Debug: In ra đỉnh đang xử lý và khoảng cách
        print(f"Processing node {u} with distance {d}")

        if d > dist[u]:
            continue
        for e in adj[u]:
            v, w = e["v"], e["w"]
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
                # Debug: In ra thông tin khi cập nhật khoảng cách
                print(f"Updating distance of {v} to {dist[v]}")

    # Debug: In ra kết quả cuối cùng
    print(f"Final distances: {dist}")
    return dist


def prim(adj):
    start = next(iter(adj))
    visited = {start}
    edges = []
    total = 0

    pq = []
    for e in adj[start]:
        heapq.heappush(pq, (e["w"], start, e["v"]))

    while pq:
        w, u, v = heapq.heappop(pq)
        if v not in visited:
            visited.add(v)
            edges.append((u, v, w))
            total += w
            for e in adj[v]:
                if e["v"] not in visited:
                    heapq.heappush(pq, (e["w"], v, e["v"]))

    return edges, total


def kruskal(adj):
    parent = {}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    def union(a, b):
        pa, pb = find(a), find(b)
        parent[pb] = pa

    edges = []
    for u in adj:
        parent[u] = u
        for e in adj[u]:
            edges.append((e["w"], u, e["v"]))

    edges.sort()
    mst = []
    total = 0

    for w, u, v in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, w))
            total += w

    return mst, total


def floyd_warshall(adj):
    verts = list(adj.keys())
    dist = {i: {j: float("inf") for j in verts} for i in verts}

    for v in verts:
        dist[v][v] = 0

    for u in adj:
        for e in adj[u]:
            dist[u][e["v"]] = min(dist[u][e["v"]], e["w"])

    for k in verts:
        for i in verts:
            for j in verts:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


def topological_sort(adj):
    indeg = {u: 0 for u in adj}
    for u in adj:
        for e in adj[u]:
            indeg[e["v"]] += 1

    q = [u for u in indeg if indeg[u] == 0]
    topo = []

    while q:
        u = q.pop(0)
        topo.append(u)
        for e in adj[u]:
            v = e["v"]
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(topo) != len(adj):
        return None
    return topo


# =======================
# Giao diện
# =======================

input_text = st.text_area(
    "Nhập danh sách kề (JSON)",
    height=300
)

algorithm = st.selectbox(
    "Chọn thuật toán",
    [
        "BFS",
        "DFS",
        "Dijkstra",
        "Prim",
        "Kruskal",
        "Floyd-Warshall",
        "Topological Sort"
    ]
)

if st.button("Chạy thuật toán"):
    try:
        if input_text.strip().startswith("{"):     
            adj_list = json.loads(input_text)  # Dữ liệu JSON nhập vào
        else:     
            adj_list = parse_edge_list(input_text)  # Dữ liệu nhập theo dạng danh sách kề
        st.subheader("Danh sách kề")
        st.json(adj_list)

        if algorithm in ["BFS", "DFS", "Dijkstra"]:
            start = st.selectbox("Chọn đỉnh bắt đầu", list(adj_list.keys()))  # Điểm xuất phát

        if algorithm == "BFS":
            st.subheader("Kết quả BFS")
            st.write(bfs(adj_list, start))

        elif algorithm == "DFS":
            st.subheader("Kết quả DFS")
            st.write(dfs(adj_list, start))

        elif algorithm == "Dijkstra":
            st.subheader("Khoảng cách ngắn nhất")
            result = dijkstra(adj_list, start)  # Gọi thuật toán Dijkstra với điểm xuất phát
            st.json(result)

        elif algorithm == "Prim":
            mst, total = prim(adj_list)
            st.subheader("Cây khung nhỏ nhất (Prim)")
            st.write(mst)
            st.write("Tổng trọng số:", total)

        elif algorithm == "Kruskal":
            mst, total = kruskal(adj_list)
            st.subheader("Cây khung nhỏ nhất (Kruskal)")
            st.write(mst)
            st.write("Tổng trọng số:", total)

        elif algorithm == "Floyd-Warshall":
            st.subheader("Khoảng cách giữa mọi cặp đỉnh")
            st.json(floyd_warshall(adj_list))

        elif algorithm == "Topological Sort":
            topo = topological_sort(adj_list)
            if topo is None:
                st.error("Đồ thị có chu trình")
            else:
                st.subheader("Thứ tự Topological Sort")
                st.write(topo)

    except Exception as e:
        st.error("Lỗi dữ liệu đầu vào")
        st.code(str(e))
