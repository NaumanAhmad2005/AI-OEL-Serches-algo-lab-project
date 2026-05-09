from collections import deque
import heapq
import time


class Maze:
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_goal(self, state):
        return state == self.goal

    def get_neighbors(self, state):
        r, c = state
        neighbors = []
        for dr, dc, action in [(-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right")]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != 1:
                neighbors.append(((nr, nc), action))
        return neighbors


class Node:
    def __init__(self, state, parent=None, action=None, depth=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost


def reconstruct_path(node):
    path = []
    actions = []
    current = node
    while current.parent is not None:
        path.append(current.state)
        actions.append(current.action)
        current = current.parent
    path.append(current.state)
    path.reverse()
    actions.reverse()
    return path, actions


def bfs(maze):
    t0 = time.perf_counter()
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], set(), 0, 0, 0.0
    frontier = deque([start_node])
    explored = set()
    nodes_explored = 0
    while frontier:
        node = frontier.popleft()
        nodes_explored += 1
        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored, time.perf_counter() - t0
        explored.add(node.state)
        for neighbor_state, action in maze.get_neighbors(node.state):
            if neighbor_state not in explored and not any(n.state == neighbor_state for n in frontier):
                frontier.append(Node(neighbor_state, node, action, node.depth + 1))
    return None, explored, float("inf"), nodes_explored, time.perf_counter() - t0


def dfs(maze):
    t0 = time.perf_counter()
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], set(), 0, 0, 0.0
    frontier = [start_node]
    explored = set()
    nodes_explored = 0
    while frontier:
        node = frontier.pop()
        nodes_explored += 1
        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored, time.perf_counter() - t0
        if node.state in explored:
            continue
        explored.add(node.state)
        for neighbor_state, action in maze.get_neighbors(node.state):
            if neighbor_state not in explored:
                frontier.append(Node(neighbor_state, node, action, node.depth + 1))
    return None, explored, float("inf"), nodes_explored, time.perf_counter() - t0


def dls(maze, limit):
    t0 = time.perf_counter()
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], set(), 0, 0, 0.0
    frontier = [start_node]
    explored = set()
    nodes_explored = 0
    while frontier:
        node = frontier.pop()
        nodes_explored += 1
        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored, time.perf_counter() - t0
        if node.state in explored:
            continue
        explored.add(node.state)
        if node.depth < limit:
            for neighbor_state, action in maze.get_neighbors(node.state):
                if neighbor_state not in explored:
                    frontier.append(Node(neighbor_state, node, action, node.depth + 1))
    return None, explored, float("inf"), nodes_explored, time.perf_counter() - t0


def ids(maze, max_depth=50):
    t0 = time.perf_counter()
    nodes_explored_total = 0
    all_explored = set()
    for depth in range(max_depth + 1):
        path, explored, cost, nodes_explored, _ = dls(maze, depth)
        nodes_explored_total += nodes_explored
        all_explored |= explored
        if path is not None:
            return path, all_explored, cost, nodes_explored_total, time.perf_counter() - t0
    return None, all_explored, float("inf"), nodes_explored_total, time.perf_counter() - t0


def manhattan_distance(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def astar(maze):
    t0 = time.perf_counter()
    start_node = Node(maze.start, cost=0)
    if maze.is_goal(start_node.state):
        return [maze.start], set(), 0, 0, 0.0
    frontier = []
    heapq.heappush(frontier, (0, id(start_node), start_node))
    explored = set()
    nodes_explored = 0
    g_cost = {maze.start: 0}
    while frontier:
        _, _, node = heapq.heappop(frontier)
        nodes_explored += 1
        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, node.cost, nodes_explored, time.perf_counter() - t0
        if node.state in explored:
            continue
        explored.add(node.state)
        for neighbor_state, action in maze.get_neighbors(node.state):
            new_g = g_cost[node.state] + 1
            if neighbor_state not in g_cost or new_g < g_cost[neighbor_state]:
                g_cost[neighbor_state] = new_g
                h = manhattan_distance(neighbor_state, maze.goal)
                f = new_g + h
                child = Node(neighbor_state, node, action, node.depth + 1, new_g)
                heapq.heappush(frontier, (f, id(neighbor_state), child))
    return None, explored, float("inf"), nodes_explored, time.perf_counter() - t0


def run_all(maze):
    results = {}
    results["BFS"]  = bfs(maze)
    results["DFS"]  = dfs(maze)
    results["IDS"]  = ids(maze)
    results["A*"]   = astar(maze)
    return results


# ── 8 built-in mazes ────────────────────────────────────────────────────────

SAMPLE_MAZES = []

# 1) 8×8 Classic
g1 = [
    [0,0,0,0,1,0,0,0],
    [1,1,0,1,1,0,1,0],
    [0,0,0,0,0,0,1,0],
    [0,1,1,1,1,0,1,0],
    [0,0,0,1,0,0,1,0],
    [1,1,0,1,0,1,1,0],
    [0,0,0,0,0,0,0,0],
    [0,1,1,1,1,0,1,0],
]
SAMPLE_MAZES.append(("Classic 8×8", Maze(g1, (0,0), (7,7))))

# 2) 5×5 Simple
g2 = [
    [0,0,1,0,0],
    [0,1,1,0,0],
    [0,0,0,1,0],
    [0,1,0,1,0],
    [0,0,0,0,0],
]
SAMPLE_MAZES.append(("Simple 5×5", Maze(g2, (0,0), (4,4))))

# 3) 7×7 Ring
g3 = [
    [0,0,0,0,0,0,0],
    [0,1,1,1,1,1,0],
    [0,1,0,0,0,1,0],
    [0,1,0,1,0,1,0],
    [0,1,0,0,0,1,0],
    [0,1,1,1,1,1,0],
    [0,0,0,0,0,0,0],
]
SAMPLE_MAZES.append(("Ring 7×7", Maze(g3, (0,0), (6,6))))

# 4) 10×10 Zigzag
g4 = [
    [0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0],
]
SAMPLE_MAZES.append(("Zigzag 10×10", Maze(g4, (0,0), (9,9))))

# 5) 9×9 Spiral-like
g5 = [
    [0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,0],
    [0,1,0,0,0,0,0,1,0],
    [0,1,0,1,1,1,0,1,0],
    [0,1,0,1,0,1,0,1,0],
    [0,1,0,1,1,1,0,1,0],
    [0,1,0,0,0,0,0,1,0],
    [0,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0],
]
SAMPLE_MAZES.append(("Spiral 9×9", Maze(g5, (0,0), (8,8))))

# 6) 6×6 Dense walls
g6 = [
    [0,1,0,0,0,0],
    [0,1,0,1,1,0],
    [0,0,0,1,0,0],
    [0,1,1,1,0,1],
    [0,0,0,0,0,1],
    [1,1,1,1,0,0],
]
SAMPLE_MAZES.append(("Dense 6×6", Maze(g6, (0,0), (5,5))))

# 7) 12×12 Large open
g7 = [
    [0,0,0,1,0,0,0,0,0,0,0,0],
    [0,1,0,1,0,1,1,1,0,1,1,0],
    [0,1,0,0,0,0,0,1,0,0,1,0],
    [0,1,1,1,1,1,0,1,1,0,1,0],
    [0,0,0,0,0,1,0,0,0,0,1,0],
    [1,1,1,0,0,1,1,1,1,0,1,0],
    [0,0,0,0,1,0,0,0,1,0,0,0],
    [0,1,1,1,1,0,1,0,1,1,1,0],
    [0,1,0,0,0,0,1,0,0,0,1,0],
    [0,1,0,1,1,1,1,1,1,0,1,0],
    [0,0,0,1,0,0,0,0,0,0,0,0],
    [1,1,0,1,0,1,1,1,1,1,0,0],
]
SAMPLE_MAZES.append(("Large 12×12", Maze(g7, (0,0), (11,11))))

# 8) 8×8 Dead-ends
g8 = [
    [0,0,1,0,0,0,1,0],
    [1,0,1,0,1,0,1,0],
    [1,0,0,0,1,0,0,0],
    [1,1,1,0,1,1,1,0],
    [0,0,0,0,0,0,1,0],
    [0,1,1,1,1,0,1,0],
    [0,0,0,0,1,0,0,0],
    [1,1,1,0,1,1,1,0],
]
SAMPLE_MAZES.append(("Dead-ends 8×8", Maze(g8, (0,0), (7,7))))
