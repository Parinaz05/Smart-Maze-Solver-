import streamlit as st
import time
from collections import deque

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Smart Maze Solver", layout="wide")

import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- INITIALIZE SESSION STATES ---
if "phase" not in st.session_state:
    st.session_state.phase = "Setup"
    img_base64 = get_base64_image("assets/CmdrKitten.gif")

    st.markdown(f"""
    <style>
    /* Remove top spacing */
    .block-container {{
        padding-top: 0rem !important;
    }}

    /* Header styling */
    .header {{
        width: 100%;
        height: 220px;
        background-image: url("data:image/gif;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        margin: 0;
        padding: 0;
    }}
    </style>

    <div class="header"></div>
    """, unsafe_allow_html=True)
if "grid_type" not in st.session_state:
    st.session_state.grid_type = "Unweighted"
if "grid" not in st.session_state:
    st.session_state.grid = [["empty" for _ in range(8)] for _ in range(8)]
if "mode" not in st.session_state:
    st.session_state.mode = "wall"
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False
# --- THEME MAPPING ---
THEME = {
    "start": "🚪",
    "end": "🏁",
    "wall": "🌳",
    "weight": "🌊",
    "visited": "👣",   
    "path": "⭐",      
    "empty": " "
}

# --- NAVIGATION HELPER ---
def go_to_phase(phase_name):
    st.session_state.phase = phase_name
    st.session_state.solve_results = None # Clear results when switching
    st.rerun()

# --- LOGIC ENGINE: BFS ---
def get_neighbors(pos, grid):
    r, c = pos
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            if grid[nr][nc] != "wall":
                neighbors.append((nr, nc))
    return neighbors

def solve_bfs(grid):
    start_pos = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "start"), None)
    end_pos = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "end"), None)
    
    if not start_pos or not end_pos:
        return None, None

    queue = deque([start_pos])
    came_from = {start_pos: None}
    visited_order = []

    while queue:
        current = queue.popleft()
        if current == end_pos: break
            
        for neighbor in get_neighbors(current, grid):
            if neighbor not in came_from:
                came_from[neighbor] = current
                visited_order.append(neighbor)
                queue.append(neighbor)

    path = []
    if end_pos in came_from:
        curr = end_pos
        while curr is not None:
            path.append(curr)
            curr = came_from[curr]
    
    return visited_order, path[::-1]

def solve_dfs(grid):
    start = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "start"), None)
    end = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "end"), None)

    stack = [start]
    came_from = {start: None}
    visited_order = []

    while stack:
        current = stack.pop()
        if current == end:
            break

        for neighbor in get_neighbors(current, grid):
            if neighbor not in came_from:
                came_from[neighbor] = current
                visited_order.append(neighbor)
                stack.append(neighbor)

    path = []
    if end in came_from:
        curr = end
        while curr:
            path.append(curr)
            curr = came_from[curr]

    return visited_order, path[::-1]

import heapq

def get_cost(cell):
    return 5 if cell == "weight" else 1

def solve_dijkstra(grid):
    start = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "start"), None)
    end = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "end"), None)

    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    visited_order = []

    while pq:
        cost, current = heapq.heappop(pq)

        if current == end:
            break

        for neighbor in get_neighbors(current, grid):
            new_cost = cost + get_cost(grid[neighbor[0]][neighbor[1]])

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor))
                came_from[neighbor] = current
                visited_order.append(neighbor)

    path = []
    if end in came_from:
        curr = end
        while curr:
            path.append(curr)
            curr = came_from[curr]

    return visited_order, path[::-1]

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar(grid):
    start = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "start"), None)
    end = next(((r, c) for r in range(8) for c in range(8) if grid[r][c] == "end"), None)

    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    visited_order = []

    while pq:
        _, current = heapq.heappop(pq)

        if current == end:
            break

        for neighbor in get_neighbors(current, grid):
            new_cost = cost_so_far[current] + get_cost(grid[neighbor[0]][neighbor[1]])

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, end)
                heapq.heappush(pq, (priority, neighbor))
                came_from[neighbor] = current
                visited_order.append(neighbor)

    path = []
    if end in came_from:
        curr = end
        while curr:
            path.append(curr)
            curr = came_from[curr]

    return visited_order, path[::-1]


# --- GLOBAL STYLES ---
st.markdown(f"""
<style>
    /* ===== GLOBAL ===== */
    body {{
        background-color: #0B0F1A;
    }}

    .main-title {{
        font-size: 50px;
        font-weight: 600;
        text-align: center;
        background: linear-gradient(90deg, #5DADE2, #58D68D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}

    .subtitle {{
        text-align: center;
        font-size: 18px;
        color: #AAB7B8;
        margin-bottom: 25px;
    }}

    .phase-indicator {{
        text-align: center;
        color: #85C1E9;
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: 500;
    }}

    /* ===== GRID TILE ===== */
    div.main [data-testid="stBaseButton-secondary"] {{
        width: 70px !important;
        height: 70px !important;
        background: linear-gradient(145deg, #1B263B, #111827) !important;
        border: 2px solid #273746 !important;
        font-size: 30px !important;
        border-radius: 14px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: inset 0px 0px 12px rgba(0,0,0,0.6) !important;
    }}

    /* ===== HOVER ===== */
    div.main [data-testid="stBaseButton-secondary"]:hover {{
        background: linear-gradient(145deg, #273746, #1C2833) !important;
        border-color: #5DADE2 !important;
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0px 6px 18px rgba(93, 173, 226, 0.5) !important;
    }}

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background: #111827 !important;
    }}

    section[data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }}

    .sidebar-label {{
        font-weight: bold;
        color: #5DADE2;
        margin-top: 20px;
        margin-bottom: 5px;
    }}

    /* ===== CARD STYLE ===== */
    .info-box {{
        background: #17202A;
        padding: 18px;
        border-radius: 12px;
        border-left: 4px solid #5DADE2;
        margin: auto;
        max-width: 600px;   
    }}

</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAV ---
if st.session_state.phase != "Setup":
    st.sidebar.title("🎮 Navigator")

    if st.sidebar.button("🏠 Back to Home"):
        go_to_phase("Setup")

    st.sidebar.markdown("<div class='sidebar-label'>🌍 World Settings</div>", unsafe_allow_html=True)

    st.session_state.grid_type = st.sidebar.selectbox(
        "Graph Nature",
        ["Unweighted", "Weighted"]
    )

# --- PHASE 1: SETUP ---
if st.session_state.phase == "Setup":

    # 🖼 Banner Image
    col1, col2, col3 = st.columns([1,2,1])

    # TITLE
    st.markdown("<div class='main-title'>🧩 Smart Maze Solver</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='subtitle'>Design, visualize, and compare pathfinding algorithms in an interactive maze.</div>",
        unsafe_allow_html=True
    )

    # STEP TEXT
    st.markdown(
        "<p style='text-align:center; color:#58D68D; font-weight:600;'>Step 1: Start Your Maze Journey</p>",
        unsafe_allow_html=True
    )

    # CENTERED CONTAINER
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:

        # INFO BOX (NOW CENTERED + NOT FULL WIDTH)
        st.markdown("""
        <div class='info-box'>
        <b>What you can do:</b><br><br>
        • Build your own maze interactively<br>
        • Run BFS, DFS, Dijkstra, and A*<br>
        • Watch algorithms explore paths live<br>
        • Compare their performance side-by-side
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # BUTTON CENTERED
        if st.button("Start Building Your Maze", use_container_width=True):
            go_to_phase("Design")



# --- PHASE 2: DESIGN ---
elif st.session_state.phase == "Design":

    # ===== SIDEBAR =====
    st.sidebar.markdown("<div class='sidebar-label'>🖌 Brush Tool</div>", unsafe_allow_html=True)

    mode_options = ["start", "end", "wall"]
    if st.session_state.grid_type == "Weighted":
        mode_options.append("weight")

    st.session_state.mode = st.sidebar.radio(
        "Select Element:",
        mode_options,
        format_func=lambda x: f"{THEME[x]} {x.capitalize()}"
    )

    st.sidebar.divider()

    if st.sidebar.button("✅ Generate Solver", use_container_width=True):
        go_to_phase("Solve")

    if st.sidebar.button("🔄 Clear Maze", use_container_width=True):
        st.session_state.grid = [["empty" for _ in range(8)] for _ in range(8)]
        st.rerun()

    # ===== MAIN CONTENT =====

    # Title
    st.markdown("<div class='main-title'>Design Your Maze</div>", unsafe_allow_html=True)

    st.markdown(
        f"<p class='phase-indicator'>Use {THEME[st.session_state.mode]} to place elements on the grid</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ===== CENTERED SECTION =====
    _, center_col, _ = st.columns([1, 2.5, 1])

    with center_col:

        # Instructions (smaller + cleaner)
        st.markdown("""
        <div class='info-box'>
        <b>Instructions:</b><br><br>
        • Click tiles to place selected element<br>
        • Only one Start and End allowed<br>
        • Walls block movement<br>
        • Water tiles increase path cost
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Legend (collapsible → less clutter)
        with st.expander("Legend"):
            st.write("🚪 Start | 🏁 End | 🌳 Wall | 🌊 Weight | 👣 Visited | ⭐ Path")

        st.markdown("<br>", unsafe_allow_html=True)

        # ===== GRID (MAIN FOCUS) =====
        for i in range(8):
            cols = st.columns(8)
            for j in range(8):
                cell = st.session_state.grid[i][j]
                label = THEME.get(cell, " ")

                if cols[j].button(label, key=f"g-{i}-{j}"):

                    if st.session_state.mode in ["start", "end"]:
                        st.session_state.grid = [
                            ["empty" if c == st.session_state.mode else c for c in row]
                            for row in st.session_state.grid
                        ]

                    st.session_state.grid[i][j] = (
                        "empty" if st.session_state.grid[i][j] == st.session_state.mode
                        else st.session_state.mode
                    )

                    st.rerun()
# --- PHASE 3: SOLVE ---
elif st.session_state.phase == "Solve":
    st.markdown("<div class='main-title'>Search Algorithms</div>", unsafe_allow_html=True)
    if st.sidebar.button("⬅️ Back to Editor", use_container_width=True):
        go_to_phase("Design")
    
    col1, col2 = st.columns([1, 2.2])

    with col1:
        st.subheader("Configuration")
        algo = st.selectbox("Search Logic", ["BFS (Breadth-First)", "DFS (Depth-First)", "Dijkstra", "A* Search"])
        st.info({
            "BFS (Breadth-First)": "Guarantees shortest path in unweighted mazes.",
            "DFS (Depth-First)": "Fast but non-optimal paths.",
            "Dijkstra": "Best for Weighted graphs (Water/Mud).",
            "A* Search": "Optimized Dijkstra using distance heuristics."
        }[algo])
        
        if st.button("Start Solving", use_container_width=True):

            if algo == "BFS (Breadth-First)":
                visited, path = solve_bfs(st.session_state.grid)
            elif algo == "DFS (Depth-First)":
                visited, path = solve_dfs(st.session_state.grid)
            elif algo == "Dijkstra":
                visited, path = solve_dijkstra(st.session_state.grid)
            elif algo == "A* Search":
                visited, path = solve_astar(st.session_state.grid)

            if not path:
                st.error("No path found!")
            else:
                st.session_state.solve_results = {"visited": visited, "path": path}
                st.success(f"Visited: {len(visited)} | Path length: {len(path)}")

        if st.button("⚖️ Compare Algorithms"):
            st.session_state.compare_mode = True

    with col2:
        st.subheader("Game Board")

        display_grid = [row[:] for row in st.session_state.grid]
        res = st.session_state.solve_results

        if res:
            frame = 0
            placeholder = st.empty()

            # Animate visited
            for r, c in res["visited"]:
                frame += 1  # ✅ moved up

                if display_grid[r][c] == "empty":
                    display_grid[r][c] = "visited"

                with placeholder.container():
                    for i in range(8):
                        cols = st.columns(8)
                        for j in range(8):
                            cols[j].button(
                                THEME.get(display_grid[i][j], " "),
                                key=f"a-{frame}-{i}-{j}"  # ✅ FIXED
                            )
                time.sleep(0.05)

            # Animate path
            for r, c in res["path"]:
                frame += 1  # ✅ add here too

                if display_grid[r][c] not in ["start", "end"]:
                    display_grid[r][c] = "path"

                with placeholder.container():
                    for i in range(8):
                        cols = st.columns(8)
                        for j in range(8):
                            cols[j].button(
                                THEME.get(display_grid[i][j], " "),
                                key=f"p-{frame}-{i}-{j}"  # ✅ FIXED
                            )
                time.sleep(0.07)

    # ✅ FIXED INDENTATION (IMPORTANT)
    if st.session_state.compare_mode:
        st.subheader("Algorithm Comparison")

    colA, colB = st.columns(2)

    algo1 = colA.selectbox("Algorithm 1", ["BFS", "DFS", "Dijkstra", "A*"], key="a1")
    algo2 = colB.selectbox("Algorithm 2", ["BFS", "DFS", "Dijkstra", "A*"], key="a2")

    def run_algo(name):
        if name == "BFS":
            return solve_bfs(st.session_state.grid)
        elif name == "DFS":
            return solve_dfs(st.session_state.grid)
        elif name == "Dijkstra":
            return solve_dijkstra(st.session_state.grid)
        elif name == "A*":
            return solve_astar(st.session_state.grid)

    if st.button("Run Comparison"):
        v1, p1 = run_algo(algo1)
        v2, p2 = run_algo(algo2)

        colA.metric("Visited Nodes", len(v1))
        colA.metric("Path Length", len(p1))

        colB.metric("Visited Nodes", len(v2))
        colB.metric("Path Length", len(p2))
        st.write("### Insights")

        if len(p1) < len(p2):
            st.success(f"{algo1} found a shorter path.")
        elif len(p2) < len(p1):
            st.success(f"{algo2} found a shorter path.")
        else:
            st.info("Both found equal path length.")