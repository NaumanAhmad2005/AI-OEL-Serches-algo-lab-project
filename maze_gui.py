"""
AI Search-Based Maze Solver — Full Desktop GUI
UET Lahore | CSC-202L Artificial Intelligence Lab | Open Ended Lab
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
import time

from algorithms import SAMPLE_MAZES, Maze, run_all

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#0f1117"
PANEL     = "#1a1d27"
CARD      = "#22263a"
ACCENT    = "#6c63ff"
ACCENT2   = "#00d4ff"
SUCCESS   = "#00e676"
WARN      = "#ffb300"
DANGER    = "#ff5252"
FG        = "#e8eaf6"
FG2       = "#9e9ec8"
WALL      = "#cbd5e1"
OPEN      = "#0f1117"
PATH_CLR  = "#00e676"
EXP_CLR   = "#6c63ff"
START_CLR = "#ffb300"
GOAL_CLR  = "#ff5252"

ALGO_COLORS = {
    "BFS":  "#00d4ff",
    "DFS":  "#ff9f43",
    "IDS":  "#a29bfe",
    "A*":   "#00e676",
}

CELL = 36          # pixel size per maze cell (scales down for big grids)


def cell_size(maze):
    return max(12, min(CELL, 480 // max(maze.rows, maze.cols)))

def create_round_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
    points = [
        x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r,
        x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r,
        x1, y1+r, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedToggle(tk.Canvas):
    def __init__(self, parent, text, variable, value, select_color, command=None, width=220, height=36):
        super().__init__(parent, width=width, height=height, bg=PANEL, highlightthickness=0)
        self.text = text
        self.variable = variable
        self.value = value
        self.select_color = select_color
        self.command = command
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.hover = False
        self.pressed = False
        self.variable.trace_add("write", self.update_state)
        self.update_state()

    def on_hover(self, e):
        self.hover = True
        self.draw()

    def on_leave(self, e):
        self.hover = False
        self.pressed = False
        self.draw()

    def on_press(self, event):
        self.pressed = True
        self.draw()

    def on_click(self, event):
        self.pressed = False
        self.variable.set(self.value)
        if self.command:
            self.command()

    def update_state(self, *args):
        self.draw()

    def draw(self):
        self.delete("all")
        selected = (self.variable.get() == self.value)
        if selected:
            bg_color = self.select_color
            fg_color = "white"
        elif self.hover:
            bg_color = CARD
            fg_color = "white"
        else:
            bg_color = BG
            fg_color = FG2
        
        offset_y = 2 if self.pressed else 0
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        create_round_rect(self, 2, 2 + offset_y, w-2, h-2, r=16, fill=bg_color, outline=bg_color)
        self.create_text(20, h//2 + offset_y, text=self.text, anchor="w", fill=fg_color, font=("Segoe UI", 10, "bold" if selected else "normal"))

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, bg_color, command=None, width=220, height=40, font=("Segoe UI", 12, "bold"), fg_color="white"):
        super().__init__(parent, width=width, height=height, bg=PANEL, highlightthickness=0)
        self.text = text
        self.bg_color = bg_color
        self.command = command
        self.font = font
        self.fg_color = fg_color
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.hover = False
        self.pressed = False
        self.draw()

    def on_hover(self, e):
        self.hover = True
        self.draw()

    def on_leave(self, e):
        self.hover = False
        self.pressed = False
        self.draw()

    def on_press(self, e):
        self.pressed = True
        self.draw()

    def on_release(self, e):
        if self.pressed:
            self.pressed = False
            self.draw()
            if self.command:
                self.command()

    def config(self, state=None, text=None):
        if text is not None:
            self.text = text
        if state == "disabled":
            self.bg_color = CARD
            self.unbind("<Button-1>")
            self.unbind("<ButtonRelease-1>")
        else:
            self.bg_color = ACCENT
            self.bind("<Button-1>", self.on_press)
            self.bind("<ButtonRelease-1>", self.on_release)
        self.draw()

    def draw(self):
        self.delete("all")
        if self.pressed:
            fill = CARD
        elif self.hover:
            fill = ACCENT2
        else:
            fill = self.bg_color
            
        offset_y = 2 if self.pressed else 0
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        create_round_rect(self, 2, 2 + offset_y, w-2, h-2, r=16, fill=fill, outline=fill)
        self.create_text(w//2, h//2 + offset_y, text=self.text, fill=self.fg_color, font=self.font)

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color=CARD, radius=16, fit_content=False, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.fit_content = fit_content
        self.inner = tk.Frame(self, bg=bg_color)
        self.window = self.create_window(radius//2, radius//2, window=self.inner, anchor="nw")
        self.bind("<Configure>", self.on_resize)
        if fit_content:
            self.inner.bind("<Configure>", self.on_inner_resize)
            
    def on_inner_resize(self, event):
        w = event.width + self.radius
        h = event.height + self.radius
        self.config(width=w, height=h)

    def on_resize(self, event):
        self.delete("bg")
        w, h = event.width, event.height
        create_round_rect(self, 2, 2, w-2, h-2, r=self.radius, fill=self.bg_color, outline=self.bg_color, tags="bg")
        self.tag_lower("bg")
        if not self.fit_content:
            self.itemconfig(self.window, width=w - self.radius, height=h - self.radius)


class MazeSolverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Maze Solver — CSC-202L")
        self.geometry("1380x820")
        self.minsize(1100, 700)
        self.configure(bg=BG)

        self._results   = {}
        self._maze      = None
        self._sel_algo  = tk.StringVar(value="All")
        self._sel_maze  = tk.IntVar(value=0)
        self._animating = False

        self._build_ui()
        self._load_maze(0)

    # ─────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ──────────────────────────────
        top = tk.Frame(self, bg=PANEL, height=58)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        tk.Label(top, text="⬡  AI MAZE SOLVER", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(top, text="CSC-202L · UET Lahore", bg=PANEL, fg=FG2,
                 font=("Segoe UI", 10)).pack(side="left", padx=4, pady=10)

        # ── Main layout: left panel + right content ──
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)

        self._left_container = tk.Frame(main, bg=PANEL, width=260)
        self._left_container.pack(side="left", fill="y")
        self._left_container.pack_propagate(False)
        
        self._left_canvas = tk.Canvas(self._left_container, bg=PANEL, highlightthickness=0)
        self._left_canvas.pack(side="left", fill="both", expand=True, padx=(14, 0))
        
        def _bind_scroll(e):
            self.bind_all("<MouseWheel>", lambda e: self._left_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
            self.bind_all("<Button-4>", lambda e: self._left_canvas.yview_scroll(-1, "units"))
            self.bind_all("<Button-5>", lambda e: self._left_canvas.yview_scroll(1, "units"))
        def _unbind_scroll(e):
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
            
        self._left_canvas.bind("<Enter>", _bind_scroll)
        self._left_canvas.bind("<Leave>", _unbind_scroll)
        
        self._left = tk.Frame(self._left_canvas, bg=PANEL)
        self._left_canvas.create_window((0, 0), window=self._left, anchor="nw")
        self._left.bind("<Configure>", lambda e: self._left_canvas.configure(scrollregion=self._left_canvas.bbox("all")))

        self._right = tk.Frame(main, bg=BG)
        self._right.pack(side="left", fill="both", expand=True)

        self._build_left()
        self._build_right()

    # ── LEFT PANEL ────────────────────────────────
    def _build_left(self):
        p = self._left

        self._section(p, "SELECT MAZE")
        for i, (name, _) in enumerate(SAMPLE_MAZES):
            rt = RoundedToggle(p, f"  {name}", self._sel_maze, i, ACCENT, command=lambda idx=i: self._load_maze(idx))
            rt.pack(anchor="center", pady=2)

        tk.Frame(p, bg=CARD, height=1).pack(fill="x", padx=12, pady=6)
        self._section(p, "ALGORITHM")

        for algo in ["All", "BFS", "DFS", "IDS", "A*"]:
            clr = ALGO_COLORS.get(algo, ACCENT)
            rt = RoundedToggle(p, f"  {algo}", self._sel_algo, algo, clr)
            rt.pack(anchor="center", pady=2)

        tk.Frame(p, bg=CARD, height=1).pack(fill="x", padx=12, pady=6)

        self._run_btn = RoundedButton(p, text="▶  RUN", bg_color=ACCENT, command=self._run)
        self._run_btn.pack(anchor="center", pady=4)

        self._section(p, "LEGEND")
        for label, color in [("Start (S)", START_CLR), ("Goal (G)", GOAL_CLR),
                              ("Path", PATH_CLR), ("Explored", EXP_CLR),
                              ("Wall", WALL), ("Open", OPEN)]:
            row = tk.Frame(p, bg=PANEL)
            row.pack(anchor="w", padx=16, pady=1)
            tk.Frame(row, bg=color, width=14, height=14).pack(side="left")
            tk.Label(row, text=f"  {label}", bg=PANEL, fg=FG2,
                     font=("Segoe UI", 9)).pack(side="left")

        tk.Frame(p, bg=CARD, height=1).pack(fill="x", padx=12, pady=6)
        self._section(p, "CONTRIBUTIONS")
                 
        contribs = ["Nauman Ahmad", "M.Tahir", "Abshar Hussain", "Daniyal Haider"]
        for c in contribs:
            dummy = RoundedButton(p, text=f"  {c}", bg_color=BG, width=220, height=36, font=("Segoe UI", 10, "normal"), fg_color=FG2)
            dummy.unbind("<Button-1>")
            dummy.unbind("<ButtonRelease-1>")
            dummy.unbind("<Enter>")
            dummy.unbind("<Leave>")
            dummy.pack(anchor="center", pady=2)

    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL, fg=FG2,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(8, 2))

    # ── RIGHT PANEL ───────────────────────────────
    def _build_right(self):
        r = self._right

        # Custom Tabs
        self._current_tab = tk.StringVar(value="maze")
        
        tab_bar = tk.Frame(r, bg=BG)
        tab_bar.pack(fill="x", padx=10, pady=(10, 0))
        
        RoundedToggle(tab_bar, "  🗺  Maze View  ", self._current_tab, "maze", ACCENT, width=160, command=self._switch_tab).pack(side="left", padx=5)
        RoundedToggle(tab_bar, "  📊  Comparison  ", self._current_tab, "table", ACCENT, width=160, command=self._switch_tab).pack(side="left", padx=5)
        RoundedToggle(tab_bar, "  📈  Charts  ", self._current_tab, "chart", ACCENT, width=160, command=self._switch_tab).pack(side="left", padx=5)

        self._tab_container = tk.Frame(r, bg=BG)
        self._tab_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Tab 1 – Maze view
        self._tab_maze = tk.Frame(self._tab_container, bg=BG)
        
        # Tab 2 – Comparison table
        self._tab_table = tk.Frame(self._tab_container, bg=BG)

        # Tab 3 – Bar charts
        self._tab_chart = tk.Frame(self._tab_container, bg=BG)

        self._build_maze_tab()
        self._build_table_tab()
        self._build_chart_tab()
        
        self._switch_tab()

    def _switch_tab(self):
        for f in [self._tab_maze, self._tab_table, self._tab_chart]:
            f.pack_forget()
        
        sel = self._current_tab.get()
        if sel == "maze":
            self._tab_maze.pack(fill="both", expand=True)
        elif sel == "table":
            self._tab_table.pack(fill="both", expand=True)
        elif sel == "chart":
            self._tab_chart.pack(fill="both", expand=True)

    # ── TAB 1: Maze view ─────────────────────────
    def _build_maze_tab(self):
        t = self._tab_maze
        self._view_algo = tk.StringVar(value="All")

        # Status bar
        self._status_var = tk.StringVar(value="Select a maze and press ▶ RUN")
        tk.Label(t, textvariable=self._status_var, bg=CARD, fg=ACCENT2,
                 font=("Segoe UI", 10), anchor="w", padx=10).pack(fill="x", padx=10, pady=4)

        # Scrollable canvas area for maze grids
        outer = tk.Frame(t, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=4)

        self._maze_canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        self._maze_canvas.pack(side="left", fill="both", expand=True)
        
        def _bind_maze_scroll(e):
            self.bind_all("<MouseWheel>", lambda e: self._maze_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
            self.bind_all("<Button-4>", lambda e: self._maze_canvas.yview_scroll(-1, "units"))
            self.bind_all("<Button-5>", lambda e: self._maze_canvas.yview_scroll(1, "units"))
            
        def _unbind_maze_scroll(e):
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
            
        self._maze_canvas.bind("<Enter>", _bind_maze_scroll)
        self._maze_canvas.bind("<Leave>", _unbind_maze_scroll)

    # ── TAB 2: Comparison table ───────────────────
    def _build_table_tab(self):
        t = self._tab_table
        
        tk.Label(t, text="Real-Time Execution Results", bg=BG, fg=ACCENT2, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
        
        self._table_container = tk.Frame(t, bg=BG)
        self._table_container.pack(fill="x", padx=10, pady=4)
        
        tk.Label(t, text="Algorithm Properties Reference", bg=BG, fg=ACCENT2, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 2))

        # Properties info box made of rounded rows
        self._info_rf = tk.Frame(t, bg=BG)
        self._info_rf.pack(fill="x", padx=10, pady=4)

        headers = ["Algorithm", "Time Complexity", "Space Complexity", "Complete?", "Optimal?", "Strategy"]
        rows = [
            ("BFS",  "O(b^d)",     "O(b^d)",     "Yes (finite)", "Yes (unit cost)", "Level-by-level"),
            ("DFS",  "O(b^m)",     "O(bm)",       "No",           "No",              "Stack / LIFO"),
            ("IDS",  "O(b^d)",     "O(bd)",       "Yes",          "Yes (unit cost)", "Iterative depth"),
            ("A*",   "O(b^d)",     "O(b^d)",      "Yes",          "Yes (admissible h)","Best-first f=g+h"),
        ]
        
        h_rf = RoundedFrame(self._info_rf, bg_color=CARD, radius=12, fit_content=True)
        h_rf.pack(fill="x", pady=2)
        for j, h in enumerate(headers):
            tk.Label(h_rf.inner, text=h, bg=CARD, fg="white", font=("Segoe UI", 10, "bold"), width=16).grid(row=0, column=j, pady=8, padx=6)

        for row in rows:
            r_rf = RoundedFrame(self._info_rf, bg_color=PANEL, radius=12, fit_content=True)
            r_rf.pack(fill="x", pady=2)
            clr = ALGO_COLORS[row[0]]
            for j, val in enumerate(row):
                tk.Label(r_rf.inner, text=val, bg=PANEL, fg=clr if j == 0 else FG, font=("Segoe UI", 10, "bold" if j==0 else "normal"), width=16).grid(row=0, column=j, pady=8, padx=6)

    # ── TAB 3: Charts ─────────────────────────────
    def _build_chart_tab(self):
        self._chart_frame = RoundedFrame(self._tab_chart, bg_color=CARD, radius=16)
        self._chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(self._chart_frame.inner, text="Run algorithms to see charts",
                 bg=CARD, fg=FG2, font=("Segoe UI", 13)).pack(expand=True)

    # ─────────────────────────────────────────────
    def _load_maze(self, idx):
        self._maze = SAMPLE_MAZES[idx][1]
        self._results = {}
        self._status_var.set(f"Loaded: {SAMPLE_MAZES[idx][0]}  —  "
                             f"{self._maze.rows}×{self._maze.cols}  "
                             f"Start{self._maze.start} → Goal{self._maze.goal}")
        self._draw_maze_grid({}, "All")
        self._clear_table()
        self._clear_charts()

    def _run(self):
        if self._animating:
            return
        algo = self._sel_algo.get()
        self._animating = True
        self._run_btn.config(state="disabled", text="Running…")
        self._status_var.set("Running algorithms…")
        threading.Thread(target=self._worker, args=(algo,), daemon=True).start()

    def _worker(self, algo):
        maze = self._maze
        if algo == "All":
            res = run_all(maze)
        else:
            from algorithms import bfs, dfs, ids, astar
            fn = {"BFS": bfs, "DFS": dfs, "IDS": ids, "A*": astar}[algo]
            res = {algo: fn(maze)}
        self._results = res
        self.after(0, self._on_done)

    def _on_done(self):
        self._run_btn.config(state="normal", text="▶  RUN")
        self._status_var.set("Animating search...")
        
        self._animate_step = 0
        self._animate_max = 0
        self._animate_data = []
        
        for algo in self._results:
            path, explored, cost, nodes, elapsed, exp_order = self._results[algo]
            self._animate_max = max(self._animate_max, len(exp_order))
            self._animate_data.append((algo, exp_order, path))
            
        self._animating = True
        empty_results = {algo: (None, set(), 0, 0, 0, []) for algo in self._results}
        self._draw_maze_grid(empty_results, self._view_algo.get())
        self._animate_loop()

    def _animate_loop(self):
        if self._animate_step < self._animate_max:
            view = self._view_algo.get()
            current_results = {}
            for algo, exp_order, path in self._animate_data:
                limit = min(self._animate_step, len(exp_order))
                current_explored = set(exp_order[:limit])
                current_results[algo] = (None, current_explored, 0, 0, 0, [])
            self._draw_maze_grid(current_results, view, is_animation=True)
            
            step_size = max(1, self._animate_max // 50) # Make it slightly faster
            self._animate_step += step_size
            self.after(30, self._animate_loop)
        else:
            self._animating = False
            view = self._view_algo.get()
            self._draw_maze_grid(self._results, view)
            self._update_table()
            self._update_charts()
            self._status_var.set("✔  Done — see Comparison and Charts tabs")

    # ── DRAW MAZE ─────────────────────────────────
    def _refresh_maze_view(self):
        if self._results:
            self._draw_maze_grid(self._results, self._view_algo.get())
        else:
            self._draw_maze_grid({}, self._view_algo.get())

    def _draw_maze_grid(self, results, view_algo, is_animation=False):
        canvas = self._maze_canvas
        if not is_animation:
            canvas.delete("all")
            self._grid_rects = {}
        
        if self._maze is None:
            return

        maze = self._maze
        cs = cell_size(maze)

        # Decide which algos to show as panels
        if view_algo == "All" and results:
            algos_to_show = [k for k in ["BFS", "DFS", "IDS", "A*"] if k in results]
        elif view_algo != "All" and view_algo in results:
            algos_to_show = [view_algo]
        else:
            algos_to_show = []

        panel_w = maze.cols * cs + 20
        panel_h = maze.rows * cs + 44

        canvas.update_idletasks()
        cw = max(canvas.winfo_width(), panel_w * 2 + 40)
        ch = max(canvas.winfo_height(), panel_h * 2 + 40)
        q_w = cw // 2
        q_h = ch // 2
        
        canvas.config(scrollregion=(0, 0, cw, ch), width=cw, height=ch)

        def draw_panel(ox, oy, algo_name, path, explored):
            if not is_animation:
                # Panel Background
                create_round_rect(canvas, ox, oy, ox+panel_w-4, oy+panel_h-4, r=16, fill=PANEL, outline=PANEL)
                
                # Header
                color = ALGO_COLORS.get(algo_name, ACCENT)
                create_round_rect(canvas, ox, oy, ox+panel_w-4, oy+36, r=16, fill=color, outline=color)
                canvas.create_rectangle(ox, oy+16, ox+panel_w-4, oy+36, fill=color, outline="")
                
                canvas.create_text(ox + panel_w//2, oy+18,
                                   text=algo_name, fill="white",
                                   font=("Segoe UI", 11, "bold"))

            gy = oy + 42
            for r in range(maze.rows):
                for c in range(maze.cols):
                    x0, y0 = ox + c*cs + 8, gy + r*cs
                    x1, y1 = x0+cs-1, y0+cs-1
                    if maze.grid[r][c] == 1:
                        fill = WALL
                    else:
                        fill = OPEN
                    # explored
                    if explored and (r, c) in explored:
                        fill = EXP_CLR
                    # path
                    if path and (r, c) in path:
                        fill = PATH_CLR
                    # start/goal
                    if (r, c) == maze.start:
                        fill = START_CLR
                    if (r, c) == maze.goal:
                        fill = GOAL_CLR

                    if not is_animation:
                        x0, y0 = ox + c*cs + 8, gy + r*cs
                        x1, y1 = x0+cs-1, y0+cs-1
                        rect_id = canvas.create_rectangle(x0, y0, x1, y1,
                                                fill=fill, outline="#2a2e45", width=1)
                        self._grid_rects[(algo_name, r, c)] = rect_id
                        
                        if (r, c) == maze.start:
                            canvas.create_text((x0+x1)//2, (y0+y1)//2,
                                               text="S", fill="white",
                                               font=("Segoe UI", max(7, cs//3), "bold"))
                        elif (r, c) == maze.goal:
                            canvas.create_text((x0+x1)//2, (y0+y1)//2,
                                               text="G", fill="white",
                                               font=("Segoe UI", max(7, cs//3), "bold"))
                    else:
                        rect_id = self._grid_rects.get((algo_name, r, c))
                        if rect_id:
                            canvas.itemconfig(rect_id, fill=fill)

        if not algos_to_show:
            # Just draw the plain maze
            panel_w = maze.cols*cs + 20
            panel_h = maze.rows*cs + 50
            ox = max(10, (q_w - panel_w) // 2)
            oy = max(10, (q_h - panel_h) // 2)
            
            create_round_rect(canvas, ox, oy, ox+panel_w, oy+panel_h, r=16, fill=PANEL, outline=PANEL)
            create_round_rect(canvas, ox, oy, ox+panel_w, oy+36, r=16, fill=ACCENT, outline=ACCENT)
            canvas.create_rectangle(ox, oy+16, ox+panel_w, oy+36, fill=ACCENT, outline="")
            
            canvas.create_text(ox + panel_w//2, oy+18,
                               text="Maze Layout", fill="white",
                               font=("Segoe UI", 11, "bold"))
            gy = oy + 42
            for r in range(maze.rows):
                for c in range(maze.cols):
                    x0, y0 = ox + c*cs + 10, gy + r*cs
                    x1, y1 = x0+cs-1, y0+cs-1
                    fill = WALL if maze.grid[r][c] == 1 else OPEN
                    if (r, c) == maze.start: fill = START_CLR
                    if (r, c) == maze.goal:  fill = GOAL_CLR
                    canvas.create_rectangle(x0, y0, x1, y1, fill=fill,
                                            outline="#2a2e45", width=1)
                    if (r, c) == maze.start:
                        canvas.create_text((x0+x1)//2,(y0+y1)//2,
                                           text="S",fill="white",
                                           font=("Segoe UI",max(7,cs//3),"bold"))
                    elif (r, c) == maze.goal:
                        canvas.create_text((x0+x1)//2,(y0+y1)//2,
                                           text="G",fill="white",
                                           font=("Segoe UI",max(7,cs//3),"bold"))
            canvas.config(scrollregion=(0,0,maze.cols*cs+40,maze.rows*cs+60),
                          width=maze.cols*cs+40, height=maze.rows*cs+60)
        else:
            for idx, algo_name in enumerate(algos_to_show):
                row_i = idx // 2
                col_i = idx % 2
                ox = col_i * q_w + max(10, (q_w - panel_w) // 2)
                oy = row_i * q_h + max(10, (q_h - panel_h) // 2)
                path_set, explored_set = set(), set()
                if algo_name in results:
                    path, explored, cost, nodes, elapsed, _ = results[algo_name]
                    if path:    path_set    = set(path)
                    if explored: explored_set = set(explored)
                draw_panel(ox, oy, algo_name, path_set, explored_set)

    # ── TABLE ─────────────────────────────────────
    def _clear_table(self):
        for widget in getattr(self, "_table_container", tk.Frame()).winfo_children():
            widget.destroy()

    def _update_table(self):
        self._clear_table()
        
        cols = ("Algorithm", "Path Found", "Path Length", "Nodes Explored", "Time (ms)", "Complete", "Optimal")
        
        header_rf = RoundedFrame(self._table_container, bg_color=CARD, radius=12, fit_content=True)
        header_rf.pack(fill="x", pady=2)
        for i, col in enumerate(cols):
            tk.Label(header_rf.inner, text=col, bg=CARD, fg="white", font=("Segoe UI", 10, "bold"), width=15).grid(row=0, column=i, pady=8, padx=4)

        completeness = {"BFS": "Yes", "DFS": "No",  "IDS": "Yes", "A*": "Yes"}
        optimality   = {"BFS": "Yes", "DFS": "No",  "IDS": "Yes", "A*": "Yes"}
        
        for algo in ["BFS", "DFS", "IDS", "A*"]:
            if algo not in self._results:
                continue
            path, _, cost, nodes, elapsed, _ = self._results[algo]
            found = "✔ Yes" if path else "✘ No"
            cost_s = str(cost) if path else "N/A"
            ms = f"{elapsed*1000:.3f}"
            
            row_rf = RoundedFrame(self._table_container, bg_color=PANEL, radius=12, fit_content=True)
            row_rf.pack(fill="x", pady=2)
            
            vals = (algo, found, cost_s, nodes, ms, completeness[algo], optimality[algo])
            for i, val in enumerate(vals):
                fg = ALGO_COLORS.get(algo, FG) if i == 0 else FG
                tk.Label(row_rf.inner, text=val, bg=PANEL, fg=fg, font=("Segoe UI", 10, "bold" if i==0 else "normal"), width=15).grid(row=0, column=i, pady=8, padx=4)

    # ── CHARTS ────────────────────────────────────
    def _clear_charts(self):
        for w in self._chart_frame.inner.winfo_children():
            w.destroy()
        tk.Label(self._chart_frame.inner, text="Run algorithms to see charts",
                 bg=CARD, fg=FG2, font=("Segoe UI", 13)).pack(expand=True)

    def _update_charts(self):
        for w in self._chart_frame.inner.winfo_children():
            w.destroy()

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            tk.Label(self._chart_frame.inner,
                     text="Install matplotlib for charts:\n  pip3 install matplotlib",
                     bg=CARD, fg=WARN, font=("Segoe UI", 12)).pack(expand=True)
            return

        algos  = [a for a in ["BFS","DFS","IDS","A*"] if a in self._results]
        nodes  = []
        costs  = []
        times  = []
        colors = [ALGO_COLORS[a] for a in algos]

        for a in algos:
            path, _, cost, n, elapsed, _ = self._results[a]
            nodes.append(n)
            costs.append(cost if cost != float("inf") else 0)
            times.append(elapsed * 1000)

        fig = Figure(figsize=(11, 4.5), facecolor=BG)
        fig.subplots_adjust(bottom=0.2)
        axes = [fig.add_subplot(1, 3, i+1) for i in range(3)]

        data_sets = [
            (nodes, "Nodes Explored", "Nodes"),
            (costs, "Path Length",    "Steps"),
            (times, "Time (ms)",      "ms"),
        ]

        for ax, (vals, title, ylabel) in zip(axes, data_sets):
            ax.set_facecolor(CARD)
            bars = ax.bar(algos, vals, color=colors, width=0.5,
                          edgecolor=BG, linewidth=1.2)
            ax.set_title(title, color=FG, fontsize=11, fontweight="bold", pad=8)
            ax.set_ylabel(ylabel, color=FG2, fontsize=9)
            ax.tick_params(colors=FG, labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor(WALL)
            ax.yaxis.label.set_color(FG2)
            ax.xaxis.label.set_color(FG2)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + max(vals)*0.01,
                        f"{val:.1f}" if isinstance(val, float) else str(val),
                        ha="center", va="bottom", color=FG, fontsize=9)

        canvas_widget = FigureCanvasTkAgg(fig, master=self._chart_frame.inner)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill="both", expand=True,
                                           padx=10, pady=10)


if __name__ == "__main__":
    app = MazeSolverApp()
    app.mainloop()
