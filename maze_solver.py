from collections import deque
import heapq


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

    def visualize(self, path=None, explored=None, title=""):
        visual = [["  " for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 1:
                    visual[r][c] = "##"

        sr, sc = self.start
        gr, gc = self.goal
        visual[sr][sc] = " S"
        visual[gr][gc] = " G"

        if explored:
            for r, c in explored:
                if (r, c) != self.start and (r, c) != self.goal:
                    visual[r][c] = " ."

        if path:
            for r, c in path:
                if (r, c) != self.start and (r, c) != self.goal:
                    visual[r][c] = " *"

        visual[sr][sc] = " S"
        visual[gr][gc] = " G"

        if title:
            print(title)
            print("-" * (self.cols * 2 + 4))
        for row in visual:
            print(" " + "".join(row))
        print()


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
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], [], 0, 0

    frontier = deque()
    frontier.append(start_node)
    explored = set()
    nodes_explored = 0

    while frontier:
        node = frontier.popleft()
        nodes_explored += 1

        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored

        explored.add(node.state)

        for neighbor_state, action in maze.get_neighbors(node.state):
            if neighbor_state not in explored and not any(
                n.state == neighbor_state for n in frontier
            ):
                child = Node(neighbor_state, node, action, node.depth + 1)
                frontier.append(child)

    return None, explored, float("inf"), nodes_explored


def dfs(maze):
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], [], 0, 0

    frontier = [start_node]
    explored = set()
    nodes_explored = 0

    while frontier:
        node = frontier.pop()
        nodes_explored += 1

        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored

        if node.state in explored:
            continue
        explored.add(node.state)

        for neighbor_state, action in maze.get_neighbors(node.state):
            if neighbor_state not in explored and not any(
                n.state == neighbor_state for n in frontier
            ):
                child = Node(neighbor_state, node, action, node.depth + 1)
                frontier.append(child)

    return None, explored, float("inf"), nodes_explored


def dls(maze, limit):
    start_node = Node(maze.start)
    if maze.is_goal(start_node.state):
        return [maze.start], [], 0, 0

    frontier = [start_node]
    explored = set()
    nodes_explored = 0

    while frontier:
        node = frontier.pop()
        nodes_explored += 1

        if maze.is_goal(node.state):
            path, actions = reconstruct_path(node)
            return path, explored, len(path) - 1, nodes_explored

        if node.state in explored:
            continue
        explored.add(node.state)

        if node.depth < limit:
            for neighbor_state, action in maze.get_neighbors(node.state):
                if neighbor_state not in explored and not any(
                    n.state == neighbor_state for n in frontier
                ):
                    child = Node(neighbor_state, node, action, node.depth + 1)
                    frontier.append(child)

    return None, explored, float("inf"), nodes_explored


def ids(maze, max_depth=50):
    nodes_explored_total = 0
    for depth in range(max_depth + 1):
        path, explored, cost, nodes_explored = dls(maze, depth)
        nodes_explored_total += nodes_explored
        if path is not None:
            return path, explored, cost, nodes_explored_total
    return None, set(), float("inf"), nodes_explored_total


def manhattan_distance(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def astar(maze):
    start_node = Node(maze.start, cost=0)
    if maze.is_goal(start_node.state):
        return [maze.start], [], 0, 0

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
            return path, explored, node.cost, nodes_explored

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

    return None, explored, float("inf"), nodes_explored


def get_maze_from_user():
    print("Enter your maze row by row.")
    print("Use 0 for open path, 1 for wall, S for start, G for goal.")
    print("Separate values with spaces. Type 'done' when finished.")
    print("Example row: 0 0 1 0 S 0 0 G 0")
    print()

    grid = []
    start = None
    goal = None
    row_idx = 0

    while True:
        line = input(f"Row {row_idx}: ").strip()
        if line.lower() == "done":
            break
        parts = line.split()
        row = []
        for c, val in enumerate(parts):
            if val == "S":
                start = (row_idx, c)
                row.append(0)
            elif val == "G":
                goal = (row_idx, c)
                row.append(0)
            else:
                row.append(int(val))
        grid.append(row)
        row_idx += 1

    if start is None or goal is None:
        print("Error: Must define both start (S) and goal (G).")
        return None

    return Maze(grid, start, goal)


def compare_algorithms(maze, run_ids=True, ids_max_depth=50):
    results = {}

    print("\n" + "=" * 70)
    print("ALGORITHM COMPARISON")
    print("=" * 70)

    path, explored, cost, nodes = bfs(maze)
    results["BFS"] = (path, explored, cost, nodes)
    maze.visualize(
        path=path,
        explored=explored if path is None else None,
        title=f"BFS - Cost: {cost}, Nodes Explored: {nodes}",
    )
    print(f"  Path length (cost): {cost}, Nodes explored: {nodes}")
    print("-" * 70)

    path, explored, cost, nodes = dfs(maze)
    results["DFS"] = (path, explored, cost, nodes)
    maze.visualize(
        path=path,
        explored=explored if path is None else None,
        title=f"DFS - Cost: {cost}, Nodes Explored: {nodes}",
    )
    print(f"  Path length (cost): {cost}, Nodes explored: {nodes}")
    print("-" * 70)

    if run_ids:
        path, explored, cost, nodes = ids(maze, ids_max_depth)
        results["IDS"] = (path, explored, cost, nodes)
        maze.visualize(
            path=path,
            explored=explored if path is None else None,
            title=f"IDS - Cost: {cost}, Nodes Explored: {nodes}",
        )
        print(f"  Path length (cost): {cost}, Nodes explored: {nodes}")
        print("-" * 70)

    path, explored, cost, nodes = astar(maze)
    results["A*"] = (path, explored, cost, nodes)
    maze.visualize(
        path=path,
        explored=explored if path is None else None,
        title=f"A* - Cost: {cost}, Nodes Explored: {nodes}",
    )
    print(f"  Path length (cost): {cost}, Nodes explored: {nodes}")
    print("-" * 70)

    print("\n" + "=" * 70)
    print("COMPARISON TABLE")
    print("=" * 70)
    print(f"{'Algorithm':<8} {'Path Found':<12} {'Cost':<8} {'Nodes Explored':<16} {'Complete':<10} {'Optimal':<10}")
    print("-" * 70)

    algos = ["BFS", "DFS", "IDS", "A*"]
    completeness = {"BFS": "Yes", "DFS": "No", "IDS": "Yes", "A*": "Yes"}
    optimality = {"BFS": "Yes", "DFS": "No", "IDS": "Yes", "A*": "Yes"}
    for name in algos:
        if name not in results:
            continue
        path, _, cost, nodes = results[name]
        found = "Yes" if path is not None else "No"
        cost_str = str(cost) if path is not None else "N/A"
        print(
            f"{name:<8} {found:<12} {cost_str:<8} {str(nodes):<16} "
            f"{completeness[name]:<10} {optimality[name]:<10}"
        )
    print("=" * 70)

    return results


def build_sample_mazes():
    mazes = []

    grid1 = [
        [0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 0],
    ]
    start1 = (0, 0)
    goal1 = (7, 7)
    mazes.append(("Maze 1 (8x8)", Maze(grid1, start1, goal1)))

    grid2 = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    start2 = (0, 0)
    goal2 = (4, 4)
    mazes.append(("Maze 2 (5x5)", Maze(grid2, start2, goal2)))

    grid3 = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    start3 = (0, 0)
    goal3 = (6, 6)
    mazes.append(("Maze 3 (Ring 7x7)", Maze(grid3, start3, goal3)))

    return mazes


def main():
    print("=" * 70)
    print("GENERIC AI SEARCH-BASED PROBLEM SOLVER")
    print("AI Lab - Open Ended Lab")
    print("=" * 70)

    while True:
        print("\nChoose input method:")
        print("  1. Use built-in sample mazes")
        print("  2. Enter your own maze")
        print("  3. Quit")

        choice = input("\nEnter choice (1/2/3): ").strip()

        if choice == "1":
            mazes = build_sample_mazes()
            for name, maze in mazes:
                print(f"\n{'=' * 70}")
                print(f"  {name}")
                print(f"{'=' * 70}")
                print(f"  Start: {maze.start}, Goal: {maze.goal}")
                maze.visualize(title="Maze Layout:")
                compare_algorithms(maze)

        elif choice == "2":
            maze = get_maze_from_user()
            if maze:
                maze.visualize(title="Your Maze:")
                compare_algorithms(maze)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
