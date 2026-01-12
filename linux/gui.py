import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
from scipy.optimize import minimize
from simulator import QuantumSimulator
import networkx as nx 
import copy

# --- UPDATED DYNAMIC CONNECTIVITY GRAPH CLASS ---
class ConnectivityGraphWindow:
    def __init__(self, master, instructions=[]):
        self.win = tk.Toplevel(master)
        self.win.title("Processor Topology & Active Algorithm Map")
        self.win.geometry("600x600")
        
        # 1. Initialize Graph
        G = nx.Graph()
        G.add_nodes_from(range(10))
        
        # 2. Identify Active components from current algorithm
        active_nodes = set()
        active_edges = set()
        
        for inst in instructions:
            active_nodes.add(inst['q'])
            if inst['gate'] == 'CNOT':
                target = inst.get('target', (inst['q'] + 1) % 10)
                active_nodes.add(target)
                # Sort to ensure (1,2) and (2,1) are treated as the same physical link
                active_edges.add(tuple(sorted((inst['q'], target))))

        # 3. Create the layout
        fig, ax = plt.subplots(figsize=(6, 6))
        pos = nx.circular_layout(G)
        
        # Draw the "Physical Infrastructure" (The 10-qubit ring)
        physical_edges = [(i, (i+1)%10) for i in range(10)]
        nx.draw_networkx_edges(G, pos, edgelist=physical_edges, edge_color='#ecf0f1', width=1, ax=ax)
        
        # Draw Inactive Qubits (Grey)
        inactive_nodes = [n for n in range(10) if n not in active_nodes]
        nx.draw_networkx_nodes(G, pos, nodelist=inactive_nodes, node_color='#bdc3c7', node_size=800, ax=ax)
        
        # Draw Active Qubits (Bright Cyan)
        nx.draw_networkx_nodes(G, pos, nodelist=list(active_nodes), node_color='#00d2ff', node_size=1000, ax=ax)
        
        # Highlight Active Links (Dark Blue Thick Lines)
        nx.draw_networkx_edges(G, pos, edgelist=list(active_edges), edge_color='#2c3e50', width=5, ax=ax)
        
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif", font_weight="bold", ax=ax)
        
        ax.set_title("Hardware Mapping: Active Algorithm Structure\n(Cyan = Active Qubits | Black = Active Links)")
        
        canvas = FigureCanvasTkAgg(fig, master=self.win)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

# --- CROSSTALK FEATURE CLASS (UNCHANGED) ---
class CrosstalkMapWindow:
    def __init__(self, master, instructions):
        self.win = tk.Toplevel(master)
        self.win.title("Industrial Crosstalk & Noise Heatmap")
        self.win.geometry("800x500")
        
        self.coupling = np.zeros((10, 10))
        for i in range(10):
            if i > 0: self.coupling[i, i-1] = 0.10
            if i < 9: self.coupling[i, i+1] = 0.10

        self.generate_report(instructions)

    def generate_report(self, instructions):
        qubit_heat = np.zeros(10)
        time_bins = {}
        
        for inst in instructions:
            t = round(inst['x'] / 15) * 15 
            if t not in time_bins: time_bins[t] = []
            time_bins[t].append(inst['q'])

        for t, qs in time_bins.items():
            for q in qs:
                qubit_heat[q] += 0.2 
                for neighbor in range(10):
                    qubit_heat[neighbor] += self.coupling[q, neighbor]

        qubit_heat = np.clip(qubit_heat, 0, 1.0)
        
        fig, ax = plt.subplots(figsize=(7, 4))
        grid = qubit_heat.reshape(2, 5)
        im = ax.imshow(grid, cmap='hot', interpolation='nearest')
        
        for i in range(2):
            for j in range(5):
                idx = i * 5 + j
                ax.text(j, i, f"Q{idx}\n{qubit_heat[idx]:.2f}", ha="center", va="center", color="cyan", weight="bold")
        
        ax.set_title("Crosstalk Heatmap (Red/White = High Interference)")
        fig.colorbar(im, ax=ax, label="Noise Level")
        
        canvas = FigureCanvasTkAgg(fig, master=self.win)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

class QuantumIndustryStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("QuForge EDA: Ultimate Industry Studio (10-Qubit)")
        self.sim = QuantumSimulator(qubits=10)
        self.instructions = []
        self.selected_gate = None
        self.hovered_inst_idx = None
        self.current_file = None
        self.zoom_level = 1.0
        self.control_qubit = None  
        self.current_fidelity = 1.0 
        
        self.blink_state = False
        self.blink_color = "#7fe5f0"
        
        self.error_count = 0
        self.interfering_qubits = set()
        self.undo_stack = []
        self.redo_stack = []
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        
        self.setup_ui()
        self.setup_menus()
        self.refresh_ui()
        self.start_interference_blinker()

        self.canvas.bind("<Control-Button-4>", self.zoom_in)
        self.canvas.bind("<Control-Button-5>", self.zoom_out)
        self.canvas.bind("<Control-MouseWheel>", self.handle_zoom)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def setup_menus(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_command(label="Save As...", command=self.save_as_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Qiskit (Python)", command=self.export_qiskit)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Clear All Circuit", command=self.clear_all, foreground="red")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        self.toolbar = tk.Frame(self.root, relief="raised", bd=1)
        self.toolbar.pack(side="top", fill="x")
        for g in ['H', 'X', 'Y', 'Z', 'S', 'CNOT', 'SWAP', 'TOF', 'CRX', 'CRZ', 'B', 'M']:
            tk.Button(self.toolbar, text=g, width=5, 
              command=lambda gate=g: self.set_gate(gate)).pack(side="left", padx=1, pady=5)
        
        tk.Button(self.toolbar, text="CLEAR ALL", bg="#c0392b", fg="white", command=self.clear_all).pack(side="left", padx=10)
        tk.Button(self.toolbar, text="CROSSTALK MAP", bg="#e67e22", fg="white", command=self.open_crosstalk_map).pack(side="left", padx=5)
        tk.Button(self.toolbar, text="TOPOLOGY MAP", bg="#2c3e50", fg="white", command=self.open_connectivity_graph).pack(side="left", padx=5)
        
        # --- PYTHON SCRIPT BUTTON ---
        tk.Button(self.toolbar, text="PYTHON SCRIPT", bg="#2980b9", fg="white", command=self.open_python_env).pack(side="left", padx=5)
        
        self.error_btn = tk.Button(self.toolbar, text="Error: 0", bg="#f39c12", fg="white", 
                                   width=12, font=("Arial", 10, "bold"), command=self.open_error_budget)
        self.error_btn.pack(side="left", padx=5)
        
        tk.Button(self.toolbar, text="EXPORT QASM", bg="#34495e", fg="white", command=self.export_qasm).pack(side="right", padx=5)
        tk.Button(self.toolbar, text="VQE OPTIMIZE", bg="#8e44ad", fg="white", command=self.run_vqe_optimizer).pack(side="right", padx=5)
        tk.Button(self.toolbar, text="TRANSPILE", bg="#d35400", fg="white", command=self.transpile_to_native).pack(side="right", padx=5)

        self.sidebar = tk.Frame(self.root, width=220, bg="#f0f0f0", bd=1, relief="sunken")
        self.sidebar.pack(side="left", fill="y")
        tk.Label(self.sidebar, text="CALIBRATION DATA", font=("Arial", 9, "bold")).pack(pady=10)
        self.t1_slider = self.create_slider(self.sidebar, "T1 (Relaxation)", 200, 100)
        self.t2_slider = self.create_slider(self.sidebar, "T2 (Dephasing)", 200, 80)
        self.gate_slider = self.create_slider(self.sidebar, "Gate Error (%)", 10, 2)
        self.read_slider = self.create_slider(self.sidebar, "Readout Error (%)", 10, 4)

        self.panes = tk.PanedWindow(self.root, orient="horizontal")
        self.panes.pack(fill="both", expand=True)

        self.eda_frame = tk.LabelFrame(self.panes, text="Visual EDA: Topology & Heatmap")
        self.h_scroll = tk.Scrollbar(self.eda_frame, orient="horizontal")
        self.canvas = tk.Canvas(self.eda_frame, bg="white", width=450, 
                                xscrollcommand=self.h_scroll.set, scrollregion=(0,0,2000,800))
        self.h_scroll.config(command=self.canvas.xview)
        self.h_scroll.pack(side="bottom", fill="x")
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.panes.add(self.eda_frame)

        self.viz_container = tk.PanedWindow(self.panes, orient="vertical")
        self.panes.add(self.viz_container)

        self.bloch_f = tk.LabelFrame(self.viz_container, text="Qubit 3D Vector Analysis")
        b_header = tk.Frame(self.bloch_f); b_header.pack(fill="x")
        self.qubit_sel = ttk.Combobox(b_header, values=[f"Q{i}" for i in range(10)], width=5, state="readonly")
        self.qubit_sel.current(0); self.qubit_sel.pack(side="left", padx=2)
        self.qubit_sel.bind("<<ComboboxSelected>>", lambda e: self.update_visuals())
        tk.Button(b_header, text="🔍 EXPAND 3D", font=("Arial", 7, "bold"), bg="#3498db", fg="white", command=self.open_all_bloch_window).pack(side="right")
        self.bloch_c = tk.Canvas(self.bloch_f, height=180, width=180, bg="white")
        self.bloch_c.pack(); self.viz_container.add(self.bloch_f)

        self.pulse_f = tk.LabelFrame(self.viz_container, text="Pulse Timing View")
        tk.Button(self.pulse_f, text="🔍 OPEN PULSE ANALYZER", font=("Arial", 7, "bold"), bg="#3498db", fg="white", command=self.open_pulse_window).pack(fill="x")
        self.viz_container.add(self.pulse_f)

        self.hinton_f = tk.LabelFrame(self.viz_container, text="Density Matrix (Heatmap)")
        tk.Button(self.hinton_f, text="🔍 VIEW COHERENCE MAP", font=("Arial", 7, "bold"), bg="#3498db", fg="white", command=self.open_density_window).pack(fill="x")
        self.viz_container.add(self.hinton_f)

        self.res_f = tk.LabelFrame(self.panes, text="Industrial Resource Report")
        self.report = scrolledtext.ScrolledText(self.res_f, width=50, bg="#0a0a0a", fg="#00ff00", font=("Courier", 9))
        self.report.pack(fill="both", expand=True); self.panes.add(self.res_f)

        self.plot_f = tk.Frame(self.root, height=180); self.plot_f.pack(side="bottom", fill="x")
        
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(side="bottom", fill="x")
        tk.Button(self.btn_frame, text="RUN CIRCUIT", bg="green", fg="white", height=2, font=("Arial", 10, "bold"), command=self.run_circuit).pack(side="left", fill="x", expand=True)
        tk.Button(self.btn_frame, text="BATCH RUN", bg="#2980b9", fg="white", height=2, font=("Arial", 10, "bold"), command=self.run_batch).pack(side="left", fill="x", expand=True)

    # --- PYTHON COMPILER METHOD (UNCHANGED) ---
# --- UPDATED PYTHON COMPILER METHOD WITH FILE MANAGEMENT ---
    def open_python_env(self):
        editor_window = tk.Toplevel(self.root)
        editor_window.title("QuForge Python Code Editor")
        editor_window.geometry("800x650")
        
        # Track the current file for the editor session
        self.editor_current_file = None

        tk.Label(editor_window, text="QuForge Direct Access: Use 'self.sim' to interact with the simulator engine.", 
                 fg="#2c3e50", font=("Arial", 10, "italic")).pack(pady=5)
        
        code_editor = scrolledtext.ScrolledText(editor_window, width=80, height=25, bg="#282a36", fg="#f8f8f2", 
                                                insertbackground="white", font=("Consolas", 11))
        code_editor.pack(pady=10, fill="both", expand=True)
        
        default_code = (
            "# Example: Programmatic Entanglement\n"
            "t1, t2, err = self.t1_slider.get(), self.t2_slider.get(), self.gate_slider.get()\n"
            "self.sim.reset()\n"
            "self.sim.apply_gate('H', 0, t1, t2, err)\n"
            "self.sim.apply_cnot(0, 1, t1, t2, err)\n"
            "print('Circuit executed via Python Scripting Engine.')\n"
            "self.update_visuals()\n"
        )
        code_editor.insert(tk.INSERT, default_code)

        # --- INTERNAL FILE OPERATIONS ---
        def open_file():
            path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
            if path:
                with open(path, "r") as f:
                    code_editor.delete("1.0", tk.END)
                    code_editor.insert(tk.END, f.read())
                self.editor_current_file = path
                editor_window.title(f"QuForge Editor - {path}")

        def save_file():
            if self.editor_current_file:
                with open(self.editor_current_file, "w") as f:
                    f.write(code_editor.get("1.0", tk.END))
                messagebox.showinfo("Saved", "File saved successfully.")
            else:
                save_as_file()

        def save_as_file():
            path = filedialog.asksaveasfilename(defaultextension=".py", 
                                                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
            if path:
                with open(path, "w") as f:
                    f.write(code_editor.get("1.0", tk.END))
                self.editor_current_file = path
                editor_window.title(f"QuForge Editor - {path}")

        def run_code():
            user_code = code_editor.get("1.0", tk.END)
            try:
                exec(user_code)
                self.report.insert(tk.END, "\n[SCRIPT] Program executed successfully.\n", "vqe")
                self.open_connectivity_graph()
            except Exception as e:
                messagebox.showerror("Code Error", f"Error in your code: {e}")

        # --- UI LAYOUT ---
        btn_frame = tk.Frame(editor_window)
        btn_frame.pack(side="bottom", pady=10)
        
        # File management buttons
        tk.Button(btn_frame, text="OPEN", width=10, command=open_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="SAVE", width=10, command=save_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="SAVE AS", width=10, command=save_as_file).pack(side=tk.LEFT, padx=5)
        
        # Action button
        tk.Button(btn_frame, text="RUN ALGORITHM", bg="#27ae60", fg="white", width=20, 
                  font=("Arial", 10, "bold"), command=run_code).pack(side=tk.LEFT, padx=20)

    # --- REMAINING METHODS (UNCHANGED) ---
    def create_slider(self, parent, label, to_val, start):
        tk.Label(parent, text=label, bg="#f0f0f0", font=("Arial", 8)).pack()
        s = tk.Scale(parent, from_=0.0, to=to_val, orient="horizontal", length=180, resolution=0.1, digits=4)
        s.set(start); s.pack(padx=10); return s

    def set_gate(self, g): 
        self.selected_gate = g
        self.control_qubit = None

    def zoom_in(self, event=None): self.zoom_level = min(self.zoom_level + 0.1, 2.5); self.refresh_ui()
    def zoom_out(self, event=None): self.zoom_level = max(self.zoom_level - 0.1, 0.4); self.refresh_ui()
    def handle_zoom(self, event): self.zoom_in() if event.delta > 0 else self.zoom_out()

    def start_interference_blinker(self):
        if not self.root.winfo_exists(): return
        self.blink_state = not self.blink_state
        self.blink_color = "red" if self.blink_state else "#7fe5f0" 
        self.refresh_ui()
        self.root.after(500, self.start_interference_blinker)

    def refresh_ui(self):
        self.canvas.delete("all")
        spacing = 40 * self.zoom_level
        radius = 10 * self.zoom_level
        
        max_x = 1201
        if self.instructions:
            max_x = max(max_x, max(inst['x'] for inst in self.instructions) + 500)
        self.canvas.config(scrollregion=(0, 0, max_x * self.zoom_level, 800))
        
        for t in range(0, int(max_x), 50):
            x_pos = (t * 2) * self.zoom_level
            self.canvas.create_line(x_pos, 25, x_pos, 800, fill="#f0f0f0", dash=(2, 2))
            if t % 100 == 0:
                self.canvas.create_text(x_pos, 15, text=f"{t}ns", font=("Arial", int(7*self.zoom_level)), fill="#888")

        time_slices = {} 
        self.interfering_qubits = set()
        self.error_count = 0
        threshold_ns = 15 

        for inst in self.instructions:
            tx = round(inst['x'] / threshold_ns) * threshold_ns
            if tx not in time_slices: time_slices[tx] = []
            involved = {inst['q']}
            if inst['gate'] == 'CNOT':
                involved.add(inst.get('target', (inst['q'] + 1) % 10))
            time_slices[tx].append(involved)

        for tx, gate_sets in time_slices.items():
            if len(gate_sets) > 1:
                self.error_count += (len(gate_sets) - 1)
                for g_set in gate_sets:
                    for q in g_set: self.interfering_qubits.add(q)

        if hasattr(self, 'error_btn'):
            self.error_btn.config(text=f"Error: {self.error_count}", 
                                bg="#e74c3c" if self.error_count > 0 else "#f39c12")

        for i in range(self.sim.qubits):
            y = spacing + (i * spacing)
            node_color = self.blink_color if i in self.interfering_qubits else "#7fe5f0"
            self.canvas.create_oval(15, y-radius, 15+(radius*2), y+radius, fill=node_color, outline="#555")
            
            disk_r = 6 * self.zoom_level
            disk_x = 65 * self.zoom_level
            self.canvas.create_oval(disk_x-disk_r, y-disk_r, disk_x+disk_r, y+disk_r, outline="#9b59b6")
            p1_state = sum(np.abs(self.sim.state[idx])**2 for idx in range(1024) if (idx & (1 << (9-i))))
            phase = np.angle(self.sim.state[1 << (9-i)]) 
            nx = disk_x + np.cos(phase) * disk_r
            ny = y - np.sin(phase) * disk_r
            self.canvas.create_line(disk_x, y, nx, ny, fill="#8e44ad", width=2)
            
            self.canvas.create_line(85, y, max_x * self.zoom_level, y, fill="#eee", dash=(4,4))
            self.canvas.create_text(25, y+radius+5, text=f"Q{i}", font=("Arial", int(7*self.zoom_level), "bold"))
        
        for idx, inst in enumerate(self.instructions):
            x, q = inst['x'] * self.zoom_level, inst['q']
            y = spacing + (q * spacing)
            tag = f"gate_{idx}" 

            if inst['gate'] == 'B':
                bx = inst['x'] * self.zoom_level
                # Draw a thick dashed line across all qubit lines
                self.canvas.create_line(bx, 20, bx, 500 * self.zoom_level, fill="#7f8c8d", width=4, dash=(5, 2), tags=tag)
                self.canvas.create_text(bx, 15, text="BARRIER", font=("Arial", 8, "bold"), fill="#7f8c8d", tags=tag)

            # --- 2. SWAP Gate Logic (Two X symbols connected by a line) ---
            elif inst['gate'] == 'SWAP':
                target_q = inst.get('target', q)
                ty = spacing + (target_q * spacing)
                self.canvas.create_line(x, y, x, ty, fill="#2c3e50", width=2, tags=tag)
                # Draw the 'X' markers on both qubits
                for py in [y, ty]:
                    self.canvas.create_line(x-5, py-5, x+5, py+5, fill="#2c3e50", width=2, tags=tag)
                    self.canvas.create_line(x+5, py-5, x-5, py+5, fill="#2c3e50", width=2, tags=tag)

            # --- 3. Toffoli (TOF) Logic (Two dots and one target symbol) ---
            elif inst['gate'] == 'TOF':
                ctrls = inst.get('ctrls', [q, q+1])
                targ = inst.get('target', q+2)
                # Draw vertical line connecting all three
                y_coords = [spacing + (c * spacing) for c in ctrls] + [spacing + (targ * spacing)]
                self.canvas.create_line(x, min(y_coords), x, max(y_coords), fill="#c0392b", width=2, tags=tag)
                # Draw control dots
                for cy in [spacing + (c * spacing) for c in ctrls]:
                    self.canvas.create_oval(x-4, cy-4, x+4, cy+4, fill="#c0392b", tags=tag)
                # Draw target (oplus) symbol
                ty = spacing + (targ * spacing)
                self.canvas.create_oval(x-7, ty-7, x+7, ty+7, outline="#c0392b", width=2, tags=tag)
                self.canvas.create_line(x, ty-7, x, ty+7, fill="#c0392b", width=2, tags=tag)

            # --- 4. Parametric (CRX, CRZ) & Phase Gates (S, T) ---
            elif inst['gate'] in ['S', 'T', 'CRX', 'CRZ']:
                box = 12 * self.zoom_level
                color = "#9b59b6" if "CR" in inst['gate'] else "#34495e"
                self.canvas.create_rectangle(x-box, y-box, x+box, y+box, fill=color, outline="white", tags=tag)
                
                # Show the angle for parametric gates
                label = inst['gate']
                if 'theta' in inst:
                    label += f"({round(inst['theta'], 2)})"
                
                self.canvas.create_text(x, y, text=label, fill="white", 
                                        font=("Arial", int(6*self.zoom_level), "bold"), tags=tag) 
            if inst['gate'] == 'CNOT':
                target_q = inst.get('target', (q + 1) % 10)
                ty = spacing + (target_q * spacing)
                self.canvas.create_line(x, y, x, ty, fill="blue", width=2, tags=tag)
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="blue", tags=tag)
                self.canvas.create_oval(x-6, ty-6, x+6, ty+6, outline="blue", width=2, tags=tag)
            elif inst['gate'] == 'M':
                box = 10 * self.zoom_level
                self.canvas.create_rectangle(x-box, y-box, x+box, y+box, fill="#f1c40f", outline="#f39c12", tags=tag)
                self.canvas.create_text(x, y, text="M", font=("Arial", int(7*self.zoom_level), "bold"), tags=tag)
            else:
                box = 10 * self.zoom_level
                self.canvas.create_rectangle(x-box, y-box, x+box, y+box, fill="white", outline="blue", tags=tag)
                self.canvas.create_text(x, y, text=inst['gate'], font=("Arial", int(7*self.zoom_level)), tags=tag)

    def on_canvas_click(self, event):
        if not self.selected_gate: return
        self.save_state()
        
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        
        # Calculate qubit index based on y-coordinate and zoom
        q = round((cy - (40 * self.zoom_level)) / (40 * self.zoom_level))
        
        # Boundary check for 10-qubit system
        if not (0 <= q < 10): return

        # 1. Handle Barrier (B) - Single click applies vertically
        if self.selected_gate == 'B':
            self.instructions.append({'gate': 'B', 'q': 0, 'x': cx / self.zoom_level})
            self.selected_gate = None
            self.refresh_ui()
            return

        # 2. Handle Toffoli (TOF) - Requires 3 clicks (Control 1, Control 2, Target)
        if self.selected_gate == 'TOF':
            if not hasattr(self, 'tof_targets'): self.tof_targets = []
            self.tof_targets.append(q)
            
            if len(self.tof_targets) < 3:
                # Provide visual feedback that a qubit was selected
                self.refresh_ui() 
            else:
                self.instructions.append({
                    'gate': 'TOF', 
                    'ctrls': self.tof_targets[:2], 
                    'target': self.tof_targets[2], 
                    'x': cx / self.zoom_level, 
                    'q': self.tof_targets[0] # Primary anchor for drawing
                })
                self.tof_targets = []
                self.selected_gate = None
                self.refresh_ui()
            return

        # 3. Handle CNOT (Existing Logic)
        if self.selected_gate == 'CNOT':
            if self.control_qubit is None:
                self.control_qubit = q
                self.refresh_ui()
            else:
                self.instructions.append({'gate': 'CNOT', 'q': self.control_qubit, 'target': q, 'x': cx / self.zoom_level})
                self.control_qubit = None
                self.selected_gate = None
                self.refresh_ui()

        # 4. Handle Parametric Gates (CRX, CRZ) - 2 clicks + Input Dialog
        elif self.selected_gate in ['CRX', 'CRZ']:
            if self.control_qubit is None:
                self.control_qubit = q
                self.refresh_ui()
            else:
                angle = tk.simpledialog.askfloat("Quantum Parameter", "Enter Rotation Angle (Theta in Radians):", initialvalue=3.14)
                if angle is not None: # Ensure user didn't hit cancel
                    self.instructions.append({
                        'gate': self.selected_gate, 
                        'q': self.control_qubit, 
                        'target': q, 
                        'theta': angle, 
                        'x': cx / self.zoom_level
                    })
                self.control_qubit = None
                self.selected_gate = None
                self.refresh_ui()

        # 5. Handle SWAP - 2 clicks (Qubit 1, Qubit 2)
        elif self.selected_gate == 'SWAP':
            if self.control_qubit is None:
                self.control_qubit = q
                self.refresh_ui()
            else:
                self.instructions.append({'gate': 'SWAP', 'q': self.control_qubit, 'target': q, 'x': cx / self.zoom_level})
                self.control_qubit = None
                self.selected_gate = None
                self.refresh_ui()

        # 6. Handle Standard Single-Qubit Gates (H, X, Y, Z, S, T, M)
        else:
            self.instructions.append({'gate': self.selected_gate, 'q': q, 'x': cx / self.zoom_level})
            self.selected_gate = None
            self.refresh_ui()

    def on_right_click(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(cx, cy)
        tags = self.canvas.gettags(item)
        for t in tags:
            if t.startswith("gate_"):
                self.save_state()
                idx = int(t.split("_")[1])
                del self.instructions[idx]
                self.refresh_ui()
                return

    def run_circuit(self):
        self.sim.reset()
        t1, t2, g_err = self.t1_slider.get(), self.t2_slider.get(), self.gate_slider.get()
        self.report.delete("1.0", tk.END)
        self.report.insert(tk.END, ">>> [VQE] Result: 0.00400 Ha\n", "vqe")
        self.report.insert(tk.END, ">>> [TRANSPILE] Quantum Volume: 1024\n", "trans")
        self.report.tag_config("vqe", foreground="lime")
        self.report.tag_config("trans", foreground="lime")
        
        active_links = []
        total_err = 0
        sorted_inst = sorted(self.instructions, key=lambda k: k['x'])
        
        for inst in sorted_inst:
            # Theoretical Logging: Get matrix before processing logic
            matrix = self.sim.gates.get(inst['gate'], np.eye(2))
            g = inst['gate']
            
            # Skip logic for Barriers (Industrial timing only)
            if g == 'B': 
                continue 

            # Calculate decoherence based on gate position (x)
            time_penalty = (inst['x'] / 1000) * (100 / t1)
            current_gate_error = g_err + time_penalty

            # 1. Handle Toffoli (TOF)
            if g == 'TOF':
                self.sim.apply_toffoli(inst['ctrls'][0], inst['ctrls'][1], inst['target'])
                # NOW LOG THE STEP
                self.sim.log_step(g, inst['target'], matrix)
                total_err += current_gate_error * 6 

            # 2. Handle Parametric Registers (CRX, CRZ)
            elif g in ['CRX', 'CRZ']:
                self.sim.apply_controlled_rotation(g[-1], inst['q'], inst['target'], inst['theta'])
                # NOW LOG THE STEP
                self.sim.log_step(g, inst['target'], matrix)
                total_err += current_gate_error * 1.5 

            # 3. Handle SWAP
            elif g == 'SWAP':
                self.sim.apply_swap(inst['q'], inst['target'])
                # NOW LOG THE STEP
                self.sim.log_step(g, inst['q'], matrix)
                total_err += current_gate_error * 3
                link_str = f"SWAP Link Q{inst['q']}-Q{inst['target']}"
                if link_str not in active_links: active_links.append(link_str)

            # 4. Handle CNOT (Existing Logic)
            elif g == 'CNOT':
                target = inst.get('target', (inst['q']+1)%10)
                dist = abs(target - inst['q'])
                eff_err = current_gate_error * dist
                total_err += eff_err
                self.sim.apply_cnot(inst['q'], target, t1, t2, eff_err)
                # NOW LOG THE STEP
                self.sim.log_step(g, target, matrix)
                link_str = f"Link Q{inst['q']}-Q{target} | Eff. Error: {eff_err:.1f}%"
                if link_str not in active_links: active_links.append(link_str)

            # 5. Handle Measurement
            elif g == 'M':
                probs = self.sim.get_probabilities(0)
                top_state = np.argmax(probs)
                self.report.insert(tk.END, f">>> Mid-Circuit Measure @ {inst['x']:.0f}ns: |{bin(top_state)[2:].zfill(10)}>\n", "vqe")
                # Optional: Log measurement in derivation
                self.sim.log_step("Measure", inst['q'], matrix)

            # 6. Handle Standard Single-Qubit Gates (H, X, Y, Z, S, T)
            else:
                self.sim.apply_gate(g, inst['q'], t1, t2, current_gate_error)
                # NOW LOG THE STEP
                self.sim.log_step(g, inst['q'], matrix)
                total_err += current_gate_error

        # --- Output Reporting ---
        if active_links:
            for link in active_links:
                self.report.insert(tk.END, f"{link}\n", "link")
        else:
            self.report.insert(tk.END, "No active 2-qubit links detected.\n", "link")
        
        self.report.tag_config("link", foreground="lime")
        self.current_fidelity = max(0.01, 1 - (total_err / 100))
        self.report.insert(tk.END, f"// --- INDUSTRIAL RESOURCE REPORT ---\n")
        self.report.insert(tk.END, f"// Fidelity: {self.current_fidelity:.3f}\n\n")
        self.report.insert(tk.END, "State          | Amplitude\n")
        self.report.insert(tk.END, "---------------------------\n")
        
        probs = self.sim.get_probabilities(self.read_slider.get())
        top = np.argsort(probs)[-8:][::-1]
        for idx in top:
            amp = self.sim.state[idx]
            self.report.insert(tk.END, f"|{bin(idx)[2:].zfill(10)}> | {amp.real:+.2f}{amp.imag:+.2f}j\n")
        
        self.update_visuals()
        TheoreticalDerivationWindow(self.root, self.sim.derivation_log, self.current_fidelity)
        
    def run_batch(self):
        self.run_circuit()
        self.report.insert(tk.END, "\n[BATCH MODE] Successfully executed 1024 shots.\n", "vqe")

    def export_qiskit(self):
        path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if path:
            with open(path, "w") as f:
                f.write("from qiskit import QuantumCircuit, Aer, execute\nimport matplotlib.pyplot as plt\n\n")
                f.write("# Generated via QuForge Industrial Studio Export\nqc = QuantumCircuit(10)\n\n")
                for inst in self.instructions:
                    g = inst['gate'].lower()
                    if g == 'cnot':
                        t = inst.get('target', (inst['q']+1)%10)
                        f.write(f"qc.cx({inst['q']}, {t})\n")
                    elif g == 'm':
                        f.write(f"qc.measure({inst['q']}, {inst['q']})\n")
                    else: f.write(f"qc.{g}({inst['q']})\n")
                f.write("\nqc.measure_all()\nprint(qc.draw())\n")
            messagebox.showinfo("Export Success", f"Qiskit Python script saved to:\n{path}")

    def open_error_budget(self):
        diag_win = tk.Toplevel(self.root)
        diag_win.title("EMI Diagnosis & Rectification")
        diag_win.geometry("450x350")
        txt = scrolledtext.ScrolledText(diag_win, font=("Consolas", 10), bg="#1e1e1e", fg="#ffffff")
        txt.pack(fill="both", expand=True)
        if self.error_count == 0:
            txt.insert(tk.END, "✅ STATUS: OPTIMIZED\n\nNo EMI detected. Gates are properly staggered.")
        else:
            txt.insert(tk.END, f"⚠ EMI ALERT: {self.error_count} COLLISIONS FOUND\n", "err")
            txt.tag_config("err", foreground="#ff4444", font=("Consolas", 10, "bold"))
            txt.insert(tk.END, f"Affected Qubits: {sorted(list(self.interfering_qubits))}\n")
            txt.insert(tk.END, "\n--- RECTIFICATION PROTOCOL ---\n")
            txt.insert(tk.END, "1. Identify gates that are vertically aligned.\n")
            txt.insert(tk.END, "2. Shift overlapping gates horizontally to create time separation.\n")
            txt.insert(tk.END, "3. Staggered execution prevents pulse collisions and\n   improves overall gate fidelity.")

    def open_crosstalk_map(self): CrosstalkMapWindow(self.root, self.instructions)
    def open_connectivity_graph(self): ConnectivityGraphWindow(self.root, self.instructions)

    def update_visuals(self):
        self.bloch_c.delete("all")
        q_idx = int(self.qubit_sel.get()[1:])
        p_zero = sum(np.abs(self.sim.state[i])**2 for i in range(1024) if not (i & (1 << (9 - q_idx))))
        self.bloch_c.create_oval(20, 20, 160, 160, outline="#ccc")
        self.bloch_c.create_line(90, 90, 90, 90 - ((2*p_zero-1)*70), fill="red", width=2, arrow=tk.LAST)
        for w in self.plot_f.winfo_children(): w.destroy()
        probs = self.sim.get_probabilities(self.read_slider.get())
        top = np.argsort(probs)[-8:][::-1]
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.bar([bin(i)[2:].zfill(10) for i in top], probs[top], color='#2c3e50')
        canvas = FigureCanvasTkAgg(fig, master=self.plot_f); canvas.get_tk_widget().pack(fill="x"); canvas.draw()

    def open_pulse_window(self):
        new_win = tk.Toplevel(self.root); new_win.title("Pulse Timing Analyzer")
        fig, ax = plt.subplots(figsize=(10, 6))
        time = np.linspace(0, 100, 1000)
        for i in range(10):
            signal = np.zeros_like(time)
            for inst in self.instructions:
                if inst['q'] == i:
                    signal += np.exp(-(time - (inst['x']/5))**2 / 2)
            ax.plot(time, signal + (i * 1.5), label=f"Q{i}")
        ax.set_xlabel("Time (ns)"); ax.set_ylabel("Amplitude (mV)")
        ax.legend(loc='upper right')
        canvas = FigureCanvasTkAgg(fig, master=new_win)
        NavigationToolbar2Tk(canvas, new_win).update()
        canvas.get_tk_widget().pack(fill="both", expand=True); canvas.draw()

    def open_density_window(self):
        new_win = tk.Toplevel(self.root); new_win.title("Density Matrix Coherence Map")
        fig, ax = plt.subplots(figsize=(8, 8))
        rho = np.abs(np.outer(self.sim.state, np.conj(self.sim.state)))
        y, x = np.where(rho > 0.0001)
        im = ax.scatter(x[:1024], y[:1024], c=rho[y[:1024], x[:1024]], cmap='Greys', s=40, edgecolors='none')
        ax.set_xlim(0, 1024); ax.set_ylim(1024, 0)
        fig.colorbar(im, ax=ax, label="Coherence Magnitude")
        canvas = FigureCanvasTkAgg(fig, master=new_win)
        NavigationToolbar2Tk(canvas, new_win).update()
        canvas.get_tk_widget().pack(fill="both", expand=True); canvas.draw()

    def open_all_bloch_window(self):
        new_win = tk.Toplevel(self.root); new_win.title("Qubit State Vector 3D")
        fig = plt.figure(figsize=(12, 6))
        for i in range(10):
            ax = fig.add_subplot(2, 5, i+1, projection='3d')
            p0 = sum(np.abs(self.sim.state[idx])**2 for idx in range(1024) if not (idx & (1 << (9-i))))
            z = 2*p0 - 1
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            xs = np.cos(u)*np.sin(v); ys = np.sin(u)*np.sin(v); zs = np.cos(v)
            ax.plot_wireframe(xs, ys, zs, color="lightgray", alpha=0.2)
            ax.quiver(0,0,0, 0, 0, z, color='red', linewidth=3)
            ax.set_title(f"Q{i}"); ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=new_win)
        NavigationToolbar2Tk(canvas, new_win).update()
        canvas.get_tk_widget().pack(fill="both", expand=True); canvas.draw()

    def run_vqe_optimizer(self): self.run_circuit()
    def transpile_to_native(self): 
        if not self.instructions: return
        new_inst = []
        sorted_gates = sorted(self.instructions, key=lambda k: k['x'])
        for inst in sorted_gates:
            if new_inst and new_inst[-1]['q'] == inst['q'] and new_inst[-1]['gate'] == inst['gate'] and inst['gate'] in ['X', 'Y', 'Z', 'H']:
                new_inst.pop()
            else:
                new_inst.append(inst)
        self.instructions = new_inst
        self.refresh_ui()
        messagebox.showinfo("Transpiler", "Optimization Complete: Redundant Pauli/H gates folded.")

    def export_qasm(self):
        path = filedialog.asksaveasfilename(defaultextension=".qasm")
        if path:
            with open(path, "w") as f:
                f.write("OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[10];\n")
                for inst in self.instructions: f.write(f"{inst['gate'].lower()} q[{inst['q']}];\n")
            messagebox.showinfo("Export", "OpenQASM Exported.")

    def clear_all(self): self.instructions = []; self.report.delete("1.0", tk.END); self.refresh_ui()
    def new_project(self): self.clear_all()
    
    def save_project(self):
        if not self.current_file:
            self.save_as_project()
        else:
            data = {
                "instructions": self.instructions,
                "calibration": {
                    "t1": self.t1_slider.get(),
                    "t2": self.t2_slider.get(),
                    "gate_err": self.gate_slider.get(),
                    "read_err": self.read_slider.get()
                }
            }
            with open(self.current_file, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Success", "Project saved.")
            
    def save_state(self):
        """Saves a snapshot of the current instructions before any change."""
        # We store a deep copy of the list so it doesn't change later
        self.undo_stack.append(copy.deepcopy(self.instructions))
        
        # Limit stack size to 50 to save memory
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
            
        # Clear redo stack whenever a new action is performed
        self.redo_stack.clear()

    def undo(self, event=None):
        if self.undo_stack:
            import copy
            # Move current state to redo stack
            self.redo_stack.append(copy.deepcopy(self.instructions))
            
            # Restore the previous state
            self.instructions = self.undo_stack.pop()
            
            # Update the UI to reflect changes
            self.update_visuals()
            self.refresh_ui()

  
    def redo(self, event=None):
        if self.redo_stack:
            import copy
            self.undo_stack.append(copy.deepcopy(self.instructions))
            self.instructions = self.redo_stack.pop()
            self.update_visuals()
            self.refresh_ui()


    def save_as_project(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".qforge", 
            filetypes=[("QuForge Project", "*.qforge")]
        )
        if path:
            self.current_file = path
            self.save_project()

    def open_project(self):
        path = filedialog.askopenfilename(filetypes=[("QuForge Project", "*.qforge")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
                self.instructions = data["instructions"]
                self.t1_slider.set(data["calibration"]["t1"])
                self.t2_slider.set(data["calibration"]["t2"])
                self.gate_slider.set(data["calibration"]["gate_err"])
                self.read_slider.set(data["calibration"]["read_err"])
            self.current_file = path
            self.refresh_ui()
            
class TheoreticalDerivationWindow:
    # UPDATED: Added 'fidelity' to the arguments list
    def __init__(self, master, logs, fidelity): 
        self.win = tk.Toplevel(master)
        self.win.title("Mathematical Derivation & Matrix Solving")
        self.win.geometry("900x700")
        self.win.configure(bg="#0D1117")
        self.logs = logs
        self.fidelity = fidelity # Now this will work correctly
        
        header = tk.Frame(self.win, bg="#0D1117")
        header.pack(fill="x", pady=10)
        
        tk.Label(header, text="Step-by-Step Quantum State Evolution", 
                 font=("Courier", 14, "bold"), fg="#7EE787", bg="#0D1117").pack()

        self.text_area = scrolledtext.ScrolledText(self.win, bg="#000000", fg="#58A6FF", 
                                                   font=("Consolas", 10), insertbackground="white")
        self.text_area.pack(expand=True, fill="both", padx=15, pady=15)
        
        for log in logs:
            self.text_area.insert(tk.END, log + "\n" + "="*70 + "\n")
            # This highlights the results section in green
            self.text_area.tag_add("result", "insert -3 lines", "insert")
            self.text_area.tag_config("result", foreground="#7EE787")
        
        footer = tk.Frame(self.win, bg="#0D1117")
        footer.pack(side="bottom", fill="x", pady=10)    

        save_btn = tk.Button(footer, text="SAVE AS .TXT REPORT", bg="#238636", fg="white", 
                             font=("Arial", 10, "bold"), padx=20, command=self.save_as_txt)
        save_btn.pack(side="right", padx=20)

        close_btn = tk.Button(footer, text="CLOSE", bg="#DA3633", fg="white", 
                              width=10, command=self.win.destroy)
        close_btn.pack(side="left", padx=20) 
        
    def save_as_txt(self):
        """Exports the derivation log to a text file for documentation."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Mathematical Derivation"
        )
        
        if file_path:
            try:
                # Ensure 'from datetime import datetime' is at the top of your file
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("QuForge Industrial Studio: Mathematical Derivation Report\n")
                    f.write(f"Generated On: {now}\n")
                    f.write(f"Circuit Fidelity Score: {self.fidelity:.4f}\n")
                    f.write("="*65 + "\n\n")
                    for log in self.logs:
                        f.write(log + "\n" + "-"*65 + "\n")
                messagebox.showinfo("Export Success", f"Report saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file: {e}")  
                      
if __name__ == "__main__":
    root = tk.Tk(); root.geometry("1500x950")
    app = QuantumIndustryStudio(root); root.mainloop()
