# CSC-202L AI Lab: Final Project Report
**Project:** AI Maze Solver & Search Algorithm Visualizer
**Contributors:** Nauman Ahmad, M.Tahir, Abshar Hussain, Daniyal Haider

---

## 1. Project Overview
The objective of this Open Ended Lab (OEL) project was to design and implement a comprehensive graphical application capable of solving complex mazes using foundational Artificial Intelligence search strategies. We successfully transitioned from a standard command-line grid solver into a fully-fledged, professionally styled desktop application that compares algorithmic performance in real-time.

## 2. Implemented Algorithms
The core engine of the application relies on four distinct search algorithms. Each has been heavily optimized and tracks its "exploration order" to allow the GUI to visualize the search progressively.

1. **Breadth-First Search (BFS)**: Implemented using `collections.deque` for $O(1)$ pop operations. It evaluates the maze radially and is guaranteed to find the shortest path, but at the cost of high memory usage ($O(b^d)$).
2. **Depth-First Search (DFS)**: Implemented via a standard LIFO stack. It dives deep into paths until hitting dead-ends. It is memory efficient ($O(bm)$) but generally yields highly sub-optimal pathing.
3. **Iterative Deepening Search (IDS)**: Merges the memory efficiency of DFS with the optimality of BFS by incrementally increasing the depth limit of a standard DFS.
4. **A* Search (A-Star)**: Implemented using Python's `heapq` to create a priority queue. It uses the Manhattan Distance heuristic ($f(n) = g(n) + h(n)$) to intelligently "pull" the search towards the goal, drastically reducing the number of nodes explored.

## 3. Libraries & Technologies Used
To ensure the application remained lightweight and easily installable while feeling like a modern desktop app, we utilized the following stack:

### Standard Libraries
- **`tkinter`**: The foundational GUI framework. We opted out of using raw `ttk` widgets and instead utilized the `tkinter.Canvas` extensively. This allowed us to build custom `RoundedFrame` and `RoundedToggle` components, creating a highly polished, dark-themed UI that avoids the clunky look of native window applications.
- **`threading`**: Utilized to separate the heavy algorithmic computations from the main GUI loop. This ensures the application remains responsive (e.g., hover animations still work) while solving massive 20x20 labyrinths.
- **`time`**: Used for high-precision benchmarking (`time.perf_counter()`) to accurately compare how many milliseconds each algorithm takes to solve a maze.
- **`collections` & `heapq`**: Essential data structures utilized to ensure the algorithms hit their theoretical Big-O time complexities.

### External Libraries
- **`matplotlib`**: We integrated Matplotlib directly into the Tkinter window via `FigureCanvasTkAgg`. This is exclusively used in the "Charts" tab to dynamically render visual Bar Charts comparing execution time and node exploration counts side-by-side upon the completion of a run.

## 4. Key Architectural Updates
During the final phases of development, the application was completely overhauled with the following advanced features:

- **Flicker-Free Animation Engine**: Instead of destroying and rebuilding the maze grid on every frame (which causes severe blinking), the application caches the `tk.Canvas` rectangle IDs and uses `itemconfig` to solely update the colors of the specific nodes being explored. This creates a buttery smooth, incredibly fast step-by-step visualization.
- **Dynamic Quadrant Layout**: When comparing all 4 algorithms at once, the GUI calculates the maximum available window width and intelligently divides the screen into a 2x2 grid. The mazes are automatically center-aligned inside their respective quadrants.
- **Pill-Style Data Tables**: Standard rigid tables were removed in favor of floating, rounded rows. Furthermore, we integrated native mouse-wheel scrolling bindings (`<Button-4>`, `<Button-5>`, and `<MouseWheel>`) across the application to ensure clean navigation without the visual clutter of scrollbars.

## 5. Conclusion
This project successfully demonstrates the practical differences between uninformed (BFS, DFS, IDS) and informed (A*) search strategies. By visualizing them simultaneously on the exact same complex topographies, users can immediately recognize the extreme efficiency benefits of heuristic-based pathfinding algorithms.
