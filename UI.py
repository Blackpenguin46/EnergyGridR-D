import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from typing import Dict, List, Tuple, Any, Optional
import os
import random
import sys


class Node:
    def __init__(self, node_type: str, canvas: tk.Canvas, x: int, y: int, energy: float = 0):
        self.node_type = node_type
        self.canvas = canvas
        self.size = 50
        self.energy = energy  # Set energy before drawing
        self.image = self.load_image(node_type)
        self.item = self.draw(x, y)
        print(f"Node created: type={node_type}, position=({x}, {y}), item={self.item}, energy={self.energy}")

    def load_image(self, node_type: str) -> Optional[ImageTk.PhotoImage]:
        image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
        image_filename = GridApp.NODE_IMAGES.get(node_type)

        if image_filename:
            image_path = os.path.join(image_dir, image_filename)
            try:
                pil_image = Image.open(image_path).resize((self.size, self.size))
                return ImageTk.PhotoImage(pil_image)
            except Exception as e:
                print(f"Error loading image for {node_type}: {e}")
        return None

    def draw(self, x: int, y: int) -> Optional[int]:
        if self.image:
            item = self.canvas.create_image(x, y, image=self.image, anchor=tk.NW, tags=(self.node_type, "node"))
        else:
            item = self.canvas.create_rectangle(x, y, x + self.size, y + self.size, fill="gray",
                                                tags=(self.node_type, "node"))

        self.canvas.create_text(x + self.size // 2, y + self.size + 10,
                                text=f"{self.energy:.1f}",
                                tags=("energy", f"energy_{item}"))
        print(f"{'Image' if self.image else 'Rectangle'} drawn on canvas: item={item}, position=({x}, {y})")
        return item

    def update_energy(self, energy: float):
        self.energy = energy
        self.canvas.itemconfig(f"energy_{self.item}", text=f"{self.energy:.1f}")


class GridSimulator:
    def __init__(self, grid_topology: Dict[str, Any]):
        self.grid_topology = grid_topology

    def simulate_performance(self) -> Dict[str, float]:
        total_energy = sum(node.energy for node in self.grid_topology['nodes'] if
                           node.node_type in ["Generator", "Coal Plant", "Natural Gas", "Nuclear Plant", "Petroleum",
                                              "Hydro"])
        total_demand = sum(
            node.energy for node in self.grid_topology['nodes'] if node.node_type in ["City", "Building"])
        efficiency = self.calculate_path_efficiency()
        load_balance = min(1.0, total_energy / (total_demand + 0.001))  # Avoid division by zero
        return {
            "total_energy_output": total_energy * efficiency,
            "total_energy_demand": total_demand,
            "average_efficiency": efficiency * 100,
            "load_balance": load_balance * 100
        }

    def calculate_path_efficiency(self) -> float:
        if not self.grid_topology['connections']:
            return 0.5  # Base efficiency if no connections

        total_efficiency = 0
        connection_count = len(self.grid_topology['connections'])

        for start, end in self.grid_topology['connections']:
            start_node = next((node for node in self.grid_topology['nodes'] if node.item == start), None)
            end_node = next((node for node in self.grid_topology['nodes'] if node.item == end), None)

            if start_node and end_node:
                energy_diff = abs(start_node.energy - end_node.energy)
                connection_efficiency = 1 - (energy_diff / max(abs(start_node.energy), abs(end_node.energy), 1))
                total_efficiency += connection_efficiency

        return total_efficiency / connection_count if connection_count > 0 else 0.5

    def perform_security_assessment(self) -> Dict[str, Any]:
        vulnerability_score = random.uniform(1, 10)
        suggestions = [
            "Implement advanced encryption",
            "Upgrade firewall systems",
            "Conduct regular security audits"
        ]
        return {
            "vulnerability_score": round(vulnerability_score, 2),
            "suggestions": random.sample(suggestions, k=2)
        }

    def export_log(self) -> str:
        log_file = "grid_simulation_log.txt"
        with open(log_file, "w") as f:
            f.write(f"Grid Topology:\n{self.grid_topology}\n")
            f.write(f"Performance: {self.simulate_performance()}\n")
            f.write(f"Security Assessment: {self.perform_security_assessment()}\n")
        return log_file


class GridApp:
    GRID_SIZE: int = 50
    NODE_IMAGES: Dict[str, str] = {
        "Generator": "generator.png",
        "Substation": "substation.png",
        "City": "city.png",
        "Building": "building.png",
        "Coal Plant": "coalplant.png",
        "Natural Gas": "naturalgas.png",
        "Nuclear Plant": "nuclearplant.png",
        "Petroleum": "petroleum.png",
        "Hydro": "hydro.png"
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_menu()
        self.create_canvas()
        self.create_output_label()
        self.bind_events()
        self.canvas.image_references = {}

    def setup_window(self):
        self.root.title("Energy Grid Simulator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#2b2b2b")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", background="#4CAF50", foreground="white", font=('Helvetica', 10, 'bold'),
                             padding=5)
        self.style.map("TButton", background=[('active', '#45a049')])

    def setup_variables(self):
        self.grid_topology: Dict[str, Any] = {'nodes': [], 'connections': []}
        self.node_type_var: tk.StringVar = tk.StringVar(value="Generator")
        self.node_coords: Dict[int, Tuple[int, int]] = {}
        self.drag_data: Dict[str, Any] = {"x": 0, "y": 0, "item": None}
        self.connection_mode: bool = False
        self.delete_mode: bool = False
        self.delete_connection_mode: bool = False
        self.connection_start: Optional[int] = None
        self.is_drawing_grid: bool = False

    def create_menu(self):
        menu_frame = ttk.Frame(self.root, style="TFrame")
        menu_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        node_type_menu = ttk.Combobox(menu_frame, textvariable=self.node_type_var,
                                      values=list(self.NODE_IMAGES.keys()),
                                      state="readonly", width=15)
        node_type_menu.pack(side=tk.LEFT, padx=5)

        ttk.Button(menu_frame, text="Add Node", command=self.toggle_add_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Connect Nodes", command=self.toggle_connection_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Delete Node", command=self.toggle_delete_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Delete Connection", command=self.toggle_delete_connection_mode).pack(side=tk.LEFT,
                                                                                                          padx=2)
        ttk.Button(menu_frame, text="Set Energy", command=self.set_node_energy).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Simulate", command=self.simulate_performance).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Security Check", command=self.perform_security_assessment).pack(side=tk.LEFT,
                                                                                                     padx=2)
        ttk.Button(menu_frame, text="Export Log", command=self.export_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="Exit", command=self.root.quit, style="Danger.TButton").pack(side=tk.RIGHT, padx=5)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.root.update()
        self.draw_grid()

    def create_output_label(self):
        self.output_frame = ttk.Frame(self.root, style="TFrame")
        self.output_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.output_label = ttk.Label(self.output_frame, text="Output will appear here",
                                      background="#1e1e1e", foreground="#00ff00",
                                      font=('Helvetica', 12), wraplength=self.root.winfo_width() - 20,
                                      justify=tk.LEFT, padding=(10, 10))
        self.output_label.pack(expand=True, fill=tk.BOTH)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Configure>", self.on_resize)
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.focus_set()

    def draw_grid(self):
        if self.is_drawing_grid:
            return
        self.is_drawing_grid = True

        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for x in range(0, width, self.GRID_SIZE):
            self.canvas.create_line(x, 0, x, height, fill="#3a3a3a", tags="grid")

        for y in range(0, height, self.GRID_SIZE):
            self.canvas.create_line(0, y, width, y, fill="#3a3a3a", tags="grid")

        self.is_drawing_grid = False

    def on_resize(self, event: tk.Event):
        self.root.after(100, self.draw_grid)

    def on_canvas_click(self, event: tk.Event):
        if self.connection_mode:
            self.handle_connection_click(event)
        elif self.delete_mode:
            self.handle_delete_click(event)
        elif self.delete_connection_mode:
            self.handle_delete_connection_click(event)
        else:
            self.handle_node_click(event)

    def handle_connection_click(self, event: tk.Event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if self.connection_start is None:
            self.connection_start = item
        else:
            self.add_connection(self.connection_start, item)
            self.connection_start = None

    def handle_delete_click(self, event: tk.Event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "node" in tags:
            self.remove_node(item)

    def handle_delete_connection_click(self, event: tk.Event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "connection" in tags:
            self.remove_connection(item)

    def handle_node_click(self, event: tk.Event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if self.canvas.type(item) == "image":
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
        else:
            self.add_node(event)

    def on_drag(self, event: tk.Event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.canvas.move(f"energy_{self.drag_data['item']}", dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event: tk.Event):
        if self.drag_data["item"]:
            snapped_x = round(event.x / self.GRID_SIZE) * self.GRID_SIZE
            snapped_y = round(event.y / self.GRID_SIZE) * self.GRID_SIZE
            self.canvas.coords(self.drag_data["item"], snapped_x, snapped_y)
            self.canvas.coords(f"energy_{self.drag_data['item']}", snapped_x + self.GRID_SIZE // 2,
                               snapped_y + self.GRID_SIZE + 10)
            self.update_node_position(self.drag_data["item"], snapped_x, snapped_y)
        self.drag_data["item"] = None

    def add_node(self, event: tk.Event):
        snapped_x = round(event.x / self.GRID_SIZE) * self.GRID_SIZE
        snapped_y = round(event.y / self.GRID_SIZE) * self.GRID_SIZE
        new_node = Node(self.node_type_var.get(), self.canvas, snapped_x, snapped_y)
        if new_node.item:
            self.grid_topology['nodes'].append(new_node)
            self.node_coords[new_node.item] = (snapped_x, snapped_y)
            if new_node.image:
                self.canvas.image_references[new_node.item] = new_node.image
        else:

            print(f"Failed to create node at ({snapped_x}, {snapped_y})")

    def update_node_position(self, item: int, x: int, y: int):
        for i, node in enumerate(self.grid_topology['nodes']):
            if node.item == item:
                node_type = node.node_type
                energy = node.energy
                self.grid_topology['nodes'][i] = Node(node_type, self.canvas, x, y, energy)
                self.node_coords[item] = (x, y)
                break

        self.update_connections(item, x, y)

    def remove_node(self, item: int):
        self.canvas.delete(item)
        self.canvas.delete(f"energy_{item}")
        self.grid_topology['nodes'] = [node for node in self.grid_topology['nodes'] if node.item != item]
        if item in self.node_coords:
            del self.node_coords[item]
        self.remove_connections(item)

    def toggle_add_mode(self):
        self.connection_mode = False
        self.delete_mode = False
        self.delete_connection_mode = False
        self.output_label.config(text="Click on the canvas to add a node")

    def toggle_connection_mode(self):
        self.connection_mode = not self.connection_mode
        self.delete_mode = False
        self.delete_connection_mode = False
        self.connection_start = None
        status = "ON" if self.connection_mode else "OFF"
        self.output_label.config(text=f"Connection mode: {status}")

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self.connection_mode = False
        self.delete_connection_mode = False
        status = "ON" if self.delete_mode else "OFF"
        self.output_label.config(text=f"Delete node mode: {status}")

    def toggle_delete_connection_mode(self):
        self.delete_connection_mode = not self.delete_connection_mode
        self.connection_mode = False
        self.delete_mode = False
        status = "ON" if self.delete_connection_mode else "OFF"
        self.output_label.config(text=f"Delete connection mode: {status}")

    def add_connection(self, start_item: int, end_item: int):
        if start_item != end_item:
            start_coords = self.canvas.coords(start_item)
            end_coords = self.canvas.coords(end_item)
            if start_coords and end_coords:
                start_x, start_y = start_coords[0] + self.GRID_SIZE // 2, start_coords[1] + self.GRID_SIZE // 2
                end_x, end_y = end_coords[0] + self.GRID_SIZE // 2, end_coords[1] + self.GRID_SIZE // 2
                line = self.canvas.create_line(start_x, start_y, end_x, end_y,
                                               fill="#4CAF50", width=2, tags="connection")
                self.canvas.tag_lower(line)
                self.grid_topology['connections'].append((start_item, end_item))

    def remove_connection(self, item: int):
        self.canvas.delete(item)
        self.grid_topology['connections'] = [
            (start, end) for start, end in self.grid_topology['connections']
            if self.canvas.find_withtag(start) and self.canvas.find_withtag(end)
        ]

    def update_connections(self, item: int, x: int, y: int):
        connections_to_update = [conn for conn in self.canvas.find_withtag("connection")
                                 if item in self.canvas.find_overlapping(*self.canvas.coords(conn))]
        for conn in connections_to_update:
            coords = self.canvas.coords(conn)
            if coords[0] == x and coords[1] == y:
                self.canvas.coords(conn, x + self.GRID_SIZE // 2, y + self.GRID_SIZE // 2, coords[2], coords[3])
            else:
                self.canvas.coords(conn, coords[0], coords[1], x + self.GRID_SIZE // 2, y + self.GRID_SIZE // 2)

    def remove_connections(self, item: int):
        connections_to_remove = [conn for conn in self.canvas.find_withtag("connection")
                                 if item in self.canvas.find_overlapping(*self.canvas.coords(conn))]
        for conn in connections_to_remove:
            self.canvas.delete(conn)
        self.grid_topology['connections'] = [
            (start, end) for start, end in self.grid_topology['connections']
            if start != item and end != item
        ]

    def set_node_energy(self):
        item = self.canvas.find_withtag("current")[0]
        node = next((n for n in self.grid_topology['nodes'] if n.item == item), None)
        if node:
            energy = simpledialog.askfloat("Set Energy", f"Enter energy value for {node.node_type}:",
                                           initialvalue=node.energy)
            if energy is not None:
                node.update_energy(energy)

    def simulate_performance(self):
        if not self.grid_topology['nodes']:
            messagebox.showwarning("Simulation Error", "No grid topology has been defined.")
            return
        simulator = GridSimulator(self.grid_topology)
        performance = simulator.simulate_performance()
        result = "Performance Metrics:\n\n"
        result += f"Energy Output: {performance['total_energy_output']:.2f}W\n"
        result += f"Energy Demand: {performance['total_energy_demand']:.2f}W\n"
        result += f"Efficiency: {performance['average_efficiency']:.2f}%\n"
        result += f"Load Balance: {performance['load_balance']:.2f}%\n\n"

        efficiency_rating = "Efficient" if performance['average_efficiency'] > 70 else "Inefficient"
        result += f"Path Efficiency: {efficiency_rating}"

        self.output_label.config(text=result)

    def perform_security_assessment(self):
        if not self.grid_topology['nodes']:
            messagebox.showwarning("Security Error", "No grid topology has been defined.")
            return
        simulator = GridSimulator(self.grid_topology)
        security = simulator.perform_security_assessment()
        result = f"Security Assessment:\n"
        result += f"Vulnerability Score: {security['vulnerability_score']:.2f}/10\n"
        result += f"Suggestions:\n"
        for suggestion in security['suggestions']:
            result += f"- {suggestion}\n"
        self.output_label.config(text=result)

    def export_log(self):
        if not self.grid_topology['nodes']:
            messagebox.showwarning("Export Error", "No grid topology has been defined.")
            return
        simulator = GridSimulator(self.grid_topology)
        log_file = simulator.export_log()
        messagebox.showinfo("Success", f"Log exported.\nLog File: {log_file}")


# This line is important for importing the GridApp class in app.py
__all__ = ['GridApp']

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()