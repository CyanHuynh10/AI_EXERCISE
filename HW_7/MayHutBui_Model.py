#https://github.com/CyanHuynh10/AI_EXERCISE

import tkinter as tk
from tkinter import ttk
import random
from collections import deque
import heapq
from PIL import Image, ImageTk

class MayHutBui:
    def __init__(self, root):
        self.root = root
        self.root.title("Model Máy hút bụi")
        self.root.geometry("1100x600") 
        self.root.configure(bg="#f4f5f5") 
        
        self.grid_size = 5
        self.cell_size = 100
        self.is_stopped = False
        self.is_running = False
        self.initial_dirty_cells = set()
        self.dirty_cells = set()
        self.rectangles = {}
        self.robot_id = None
        self.path = []
        
        self.setup_ui()
        self.change_matrix()

    def setup_ui(self):
        # --- KHUNG BÊN TRÁI (Khu vực DEMO) ---
        left_border_frame = tk.Frame(self.root, bg="black", bd=1)
        left_border_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=20)
        
        demo_bg_frame = tk.Frame(left_border_frame, bg="#9ba0a6") 
        demo_bg_frame.pack(fill=tk.BOTH, expand=True)
        
        demo_header = tk.Frame(demo_bg_frame, bg="#82888f", height=35)
        demo_header.pack(side=tk.TOP, fill=tk.X)
        demo_header.pack_propagate(False) 
        
        demo_label = tk.Label(demo_header, text="DEMO", font=("Arial", 14, "bold"), bg="#82888f", fg="black")
        demo_label.pack(expand=True)
        
        canvas_width = self.grid_size * self.cell_size
        canvas_height = self.grid_size * self.cell_size
        self.canvas_frame = tk.Frame(demo_bg_frame, bg="#9ba0a6")
        self.canvas_frame.pack(expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_width, height=canvas_height, bg="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(pady=10)
        
        # --- KHUNG BÊN PHẢI (Khu vực Điều khiển) ---
        right_frame = tk.Frame(self.root, bg="#f4f5f5", width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=20)
        right_frame.pack_propagate(False) 
        
        btn_frame = tk.Frame(right_frame, bg="#f4f5f5")
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.run_btn = tk.Button(btn_frame, text="▶ Run", font=("Arial", 11), bg="#d4edda", fg="black", relief=tk.RIDGE, bd=1, height=2, command=self.run_algorithm)
        self.run_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.stop_btn = tk.Button(btn_frame, text="■ Stop", font=("Arial", 11), bg="white", fg="black", relief=tk.RIDGE, bd=1, height=2, command=self.stop_algorithm)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 2))

        self.change_btn = tk.Button(btn_frame, text="⟳ Change", font=("Arial", 11), bg="#cce5ff", fg="black", relief=tk.RIDGE, bd=1, height=2, command=self.change_matrix)
        self.change_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 2))

        self.reset_btn = tk.Button(btn_frame, text="↺ Reset", font=("Arial", 11), bg="#ffeeba", fg="black", relief=tk.RIDGE, bd=1, height=2, command=self.reset_environment)
        self.reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        algo_frame = tk.Frame(right_frame, bg="#f4f5f5")
        algo_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(algo_frame, text="Thuật toán:", font=("Arial", 11), bg="#f4f5f5").pack(side=tk.LEFT)
        
        self.algo_combo = ttk.Combobox(algo_frame, font=("Arial", 11), state="readonly", values=["BFS", "DFS", "IDS", "UCS"])
        self.algo_combo.current(0)
        self.algo_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="Bước đi:", font=("Arial", 11), bg="#f4f5f5", anchor='w').pack(fill=tk.X)
        
        step_frame = tk.Frame(right_frame)
        step_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        self.step_text = tk.Text(step_frame, font=("Arial", 11), bd=1, relief=tk.SOLID)
        step_scroll = ttk.Scrollbar(step_frame, command=self.step_text.yview)
        self.step_text.configure(yscrollcommand=step_scroll.set)
        
        self.step_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        step_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def load_robot_image(self):
        try:
            image = Image.open(r"D:\Cyan\2526_2_AI\MayHutBui.png")
            image = image.resize((self.cell_size - 20, self.cell_size - 20), Image.LANCZOS)
            self.tk_robot_img = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Không thể tải ảnh: {e}")
            self.tk_robot_img = None

    def change_matrix(self):
        if self.is_running:
            self.is_stopped = True
            
        self.initial_dirty_cells.clear()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                is_dirty = random.choice([True, False]) if (r, c) != (0, 0) else False
                if is_dirty:
                    self.initial_dirty_cells.add((r, c))
                    
        self.reset_environment()

    def reset_environment(self):
        if self.is_running:
            self.is_stopped = True
            
        self.canvas.delete("all")
        self.rectangles.clear()
        
        self.dirty_cells = set(self.initial_dirty_cells)
        
        for r in range(self.grid_size):
            self.rectangles[r] = {}
            for c in range(self.grid_size):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = "black" if (r, c) in self.dirty_cells else "white"
                
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.rectangles[r][c] = rect_id

        self.load_robot_image()
        center_x = self.cell_size // 2
        center_y = self.cell_size // 2
        
        if self.tk_robot_img:
            self.robot_id = self.canvas.create_image(center_x, center_y, image=self.tk_robot_img)
        else:
            self.robot_id = self.canvas.create_oval(15, 15, self.cell_size-15, self.cell_size-15, fill="red")

        self.step_text.delete(1.0, tk.END)
        self.is_stopped = False
        self.is_running = False

    def get_successors(self, state):
        r, c, dirty_tuple = state
        successors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                new_dirty = tuple(d for d in dirty_tuple if d != (nr, nc))
                successors.append(((nr, nc, new_dirty), 1)) 
        return successors

    # --- KHU VỰC THUẬT TOÁN AI ---
    def run_algorithm(self):
        if self.is_running or not self.dirty_cells:
            return
        
        self.is_running = True
        self.is_stopped = False
        self.step_text.delete(1.0, tk.END)
        
        algo = self.algo_combo.get()
        start_state = (0, 0, tuple(self.dirty_cells))
        
        final_path = []
        
        if algo == "BFS":
            final_path = self.bfs(start_state)
        elif algo == "DFS":
            final_path = self.dfs(start_state)
        elif algo == "UCS":
            final_path = self.ucs(start_state)
        elif algo == "IDS":
            final_path = self.ids(start_state)

        if final_path:
            path_coords = [(r, c) for r, c, _ in final_path]
            self.animate_step(path_coords, 1) 
        else:
            self.is_running = False

    def bfs(self, start_state):
        queue = deque([(start_state, [start_state])])
        visited = set([start_state])
        
        while queue:
            state, path = queue.popleft()
            if len(state[2]) == 0: 
                return path
            
            for next_state, cost in self.get_successors(state):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [next_state]))
        return []

    def dfs(self, start_state):
        def heuristic(state):
            r, c, dirty_tuple = state
            if not dirty_tuple:
                return 0
            return min(abs(r - dr) + abs(c - dc) for dr, dc in dirty_tuple)

        stack = [(start_state, [start_state])]
        visited = set([start_state])
        
        while stack:
            state, path = stack.pop()
            if len(state[2]) == 0:
                return path
            
            successors = self.get_successors(state)
            
            valid_successors = []
            for next_state, cost in successors:
                if next_state not in visited:
                    valid_successors.append(next_state)
            
            valid_successors.sort(key=heuristic, reverse=True)
            
            for next_state in valid_successors:
                visited.add(next_state)
                stack.append((next_state, path + [next_state]))
                
        return []

    def ucs(self, start_state):
        pq = [(0, id(start_state), start_state, [start_state])]
        visited = {}
        
        while pq:
            cost, _, state, path = heapq.heappop(pq)
            
            if len(state[2]) == 0:
                return path
            
            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost
            
            for next_state, step_cost in self.get_successors(state):
                new_cost = cost + step_cost
                if next_state not in visited or new_cost < visited[next_state]:
                    heapq.heappush(pq, (new_cost, id(next_state), next_state, path + [next_state]))
        return []

    def ids(self, start_state):
        def dls(state, path, depth, visited):
            if len(state[2]) == 0:
                return path
            if depth == 0:
                return None
            
            for next_state, cost in self.get_successors(state):
                if next_state not in visited or visited[next_state] < depth:
                    visited[next_state] = depth
                    result = dls(next_state, path + [next_state], depth - 1, visited)
                    if result is not None:
                        return result
            return None

        depth = 0
        while True:
            visited = {start_state: depth}
            result = dls(start_state, [start_state], depth, visited)
            if result is not None:
                return result
            depth += 1
            if depth > 50: 
                return []

    def stop_algorithm(self):
        self.is_stopped = True
        self.is_running = False

    def animate_step(self, path, step_idx):
        if self.is_stopped:
            self.is_running = False
            return
            
        if step_idx >= len(path):
            self.is_running = False
            return
            
        r, c = path[step_idx]
        
        self.canvas.itemconfig(self.rectangles[r][c], fill="#32a852")
        
        new_x = c * self.cell_size + (self.cell_size // 2)
        new_y = r * self.cell_size + (self.cell_size // 2)
        self.canvas.coords(self.robot_id, new_x, new_y)
        
        step_str = f"Bước {step_idx}: ({r} ; {c})\n"
        self.step_text.insert(tk.END, step_str)
        self.step_text.see(tk.END) 
        
        self.root.after(400, self.animate_step, path, step_idx + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = MayHutBui(root)
    root.mainloop()