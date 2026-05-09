# ⬡ AI Maze Solver & Algorithm Visualizer

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange?style=for-the-badge)

A fully functional, professionally styled desktop application built for the **CSC-202L Artificial Intelligence Lab (UET Lahore)**. This application visualizes and compares various search algorithms (BFS, DFS, IDS, A*) in real-time as they attempt to solve mazes of varying complexities.

---

## ✨ Features
- **Real-Time Step-by-Step Visualization**: Watch exactly how each algorithm explores the maze grid, node by node, without any flickering.
- **Dynamic Quadrant Layout**: View multiple algorithms running side-by-side in a responsive 2x2 grid layout.
- **Extensive Maze Library**: Over 10 built-in mazes ranging from simple 5x5 grids to complex 20x20 labyrinths.
- **Deep Statistical Comparison**:
  - Live execution tracking (Path Found, Path Length, Nodes Explored, Time elapsed).
  - Detailed side-by-side tables covering Time Complexity, Space Complexity, Completeness, and Optimality.
  - Automatically generated **Matplotlib Bar Charts** visualizing algorithmic performance.
- **Modern UI/UX**: Custom-built `RoundedFrame` components and "pill-style" grids to achieve a clean, dark-mode aesthetic. 

## 🧠 Supported Algorithms
1. **Breadth-First Search (BFS)**: Level-by-level exploration. Guarantees the shortest path (optimal) but requires significant memory $O(b^d)$.
2. **Depth-First Search (DFS)**: Stack-based deep exploration. Memory efficient $O(bm)$ but does not guarantee the shortest path.
3. **Iterative Deepening Search (IDS)**: Combines DFS's space efficiency with BFS's optimality by slowly increasing the depth limit.
4. **A* Search (A-Star)**: Heuristic-based search ($f(n) = g(n) + h(n)$). Uses Manhattan distance to find the optimal path incredibly efficiently.

---

## 🛠️ Tech Stack & Libraries Used
This project was built to be lightweight while maintaining a premium feel. 

- **`tkinter` (Standard Library)**: Used as the core graphical engine. It powers the custom rounded components, the main application loop, the scrolling canvases, and the grid rendering. 
- **`matplotlib`**: Used explicitly in the "Charts" tab to dynamically render performance bar charts (comparing Time taken and Nodes explored).
- **`threading` (Standard Library)**: Used to run search algorithms asynchronously so the main GUI loop never freezes while calculating paths for massive mazes.
- **`heapq` & `collections.deque` (Standard Library)**: Used to build highly optimized priority queues (for A*) and fast FIFO queues (for BFS).

---

## 🚀 Installation & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NaumanAhmad2005/AI-OEL-Serches-algo-lab-project.git
   cd AI-OEL-Serches-algo-lab-project
   ```

2. **Install required dependencies**:
   The only external dependency required is `matplotlib`.
   ```bash
   pip install matplotlib
   ```

3. **Run the Application**:
   ```bash
   python maze_gui.py
   ```
*(Note: Use `python3` if you are on a Linux/Mac environment).*

---

## 👥 Contributors
This project was proudly developed by:
- **Nauman Ahmad**
- **M.Tahir**
- **Abshar Hussain**
- **Daniyal Haider**

*Developed for the AI Lab Open Ended Lab (OEL).*
