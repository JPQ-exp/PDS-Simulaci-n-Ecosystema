import tkinter as tk
from tkinter import ttk
import numpy as np
import random

# ==========================================
# CONFIGURACIÓN INICIAL Y PARÁMETROS
# ==========================================
WIDTH, HEIGHT = 600, 600
INITIAL_HERBIVORES = 50
INITIAL_CARNIVORES = 8
NUM_FOOD = 150

# Parámetros constantes (no editables en el panel)
DECAY_H = 0.05
DECAY_C = 0.08
SPEED_H = 2.5
SPEED_C = 3.2
SPLIT_THRESH_H = 8.0
SPLIT_THRESH_C = 25.0
LIFESPAN = 1000  # Ciclos de vida

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ecosistema Emergente: Persistencia Axiomática")
        
        # --- Variables de Control (Sliders) ---
        self.fear_radius = tk.DoubleVar(value=50.0)
        self.growth_delay = tk.DoubleVar(value=40.0)
        self.digestion_rate = tk.DoubleVar(value=0.5)
        self.is_running = True

        self.setup_ui()
        
        # --- Inicialización de Entidades ---
        self.food_patches = []
        for _ in range(NUM_FOOD):
            # [x, y, timer, id_canvas]
            x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
            item_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="green", outline="")
            self.food_patches.append([x, y, 0, item_id])

        self.herbivores = [self.create_agent("H") for _ in range(INITIAL_HERBIVORES)]
        self.carnivores = [self.create_agent("C") for _ in range(INITIAL_CARNIVORES)]
        
        self.update_loop()

    def setup_ui(self):
        # Frame Principal
        main_frame = tk.Frame(self.root, bg="#222")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas de Simulación
        self.canvas = tk.Canvas(main_frame, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Panel Lateral
        panel = tk.Frame(main_frame, bg="#333", width=250)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(panel, text="PANEL DE CONTROL", fg="white", bg="#333", font=("Arial", 12, "bold")).pack(pady=10)

        # Sliders
        self.create_slider(panel, "Radio de Miedo (Sensor)", self.fear_radius, 0, 150)
        self.create_slider(panel, "Delay de Comida (Crecimiento)", self.growth_delay, 1, 200)
        self.create_slider(panel, "Tasa de Digestión", self.digestion_rate, 0.1, 2.0)

        # Estadísticas y Barras
        self.stats_label = tk.Label(panel, text="", fg="white", bg="#333", justify=tk.LEFT)
        self.stats_label.pack(pady=20)

        self.bar_h = tk.Frame(panel, bg="blue", height=20, width=0)
        self.bar_h.pack(fill=tk.X, padx=10, pady=2)
        self.bar_c = tk.Frame(panel, bg="red", height=20, width=0)
        self.bar_c.pack(fill=tk.X, padx=10, pady=2)

        tk.Button(panel, text="PAUSAR / REANUDAR", command=self.toggle_sim).pack(pady=20)

    def create_slider(self, parent, text, var, low, high):
        tk.Label(parent, text=text, fg="#aaa", bg="#333").pack()
        s = tk.Scale(parent, from_=low, to=high, orient=tk.HORIZONTAL, variable=var, 
                     bg="#333", fg="white", highlightthickness=0)
        s.pack(fill=tk.X, padx=10, pady=5)

    def create_agent(self, type):
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        color = "cyan" if type == "H" else "red"
        size = 3 if type == "H" else 6
        item_id = self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline="")
        return {
            "pos": np.array([x, y]),
            "energy": 5.0 if type == "H" else 15.0,
            "stomach": 0.0,
            "type": type,
            "id": item_id,
            "age": 0,
            "size": size
        }

    def toggle_sim(self):
        self.is_running = not self.is_running

    def wrap_torus(self, pos):
        return np.mod(pos, [WIDTH, HEIGHT])

    def get_shortest_dist(self, p1, p2):
        delta = p2 - p1
        delta = (delta + [WIDTH/2, HEIGHT/2]) % [WIDTH, HEIGHT] - [WIDTH/2, HEIGHT/2]
        return delta, np.linalg.norm(delta)

    def update_loop(self):
        if self.is_running:
            # 1. Crecimiento de comida
            for f in self.food_patches:
                if f[2] > 0:
                    f[2] -= 1
                    if f[2] <= 0:
                        self.canvas.itemconfig(f[3], state='normal')

            # 2. Lógica Herbívoros
            new_herbivores = []
            for h in self.herbivores[:]:
                # Sensor: Buscar Carnívoro más cercano para huir
                evasion_vec = np.array([0.0, 0.0])
                for c in self.carnivores:
                    diff, dist = self.get_shortest_dist(h["pos"], c["pos"])
                    if dist < self.fear_radius.get():
                        evasion_vec -= diff / (dist + 0.1)

                # Sensor: Buscar Comida
                food_vec = np.array([0.0, 0.0])
                min_fd = 999
                for f in self.food_patches:
                    if f[2] <= 0:
                        diff, dist = self.get_shortest_dist(h["pos"], np.array([f[0], f[1]]))
                        if dist < min_fd:
                            min_fd = dist
                            food_vec = diff
                
                # Movimiento
                move = (food_vec * 0.1) + (evasion_vec * 2.0)
                norm = np.linalg.norm(move)
                if norm > 0: move = (move / norm) * SPEED_H
                
                h["pos"] = self.wrap_torus(h["pos"] + move + np.random.normal(0, 0.5, 2))
                
                # Comer
                if min_fd < 5:
                    for f in self.food_patches:
                        if f[2] <= 0 and np.linalg.norm(h["pos"] - [f[0], f[1]]) < 8:
                            h["stomach"] += 2.0
                            f[2] = self.growth_delay.get()
                            self.canvas.itemconfig(f[3], state='hidden')
                            break

                # Metabolismo
                digested = min(h["stomach"], self.digestion_rate.get())
                h["stomach"] -= digested
                h["energy"] += digested - DECAY_H
                h["age"] += 1

                # Replicación
                if h["energy"] > SPLIT_THRESH_H:
                    h["energy"] /= 2
                    new_herbivores.append(self.create_agent("H"))

                # Muerte
                if h["energy"] <= 0 or h["age"] > LIFESPAN:
                    self.canvas.delete(h["id"])
                    self.herbivores.remove(h)
                else:
                    self.canvas.coords(h["id"], h["pos"][0]-h["size"], h["pos"][1]-h["size"], 
                                       h["pos"][0]+h["size"], h["pos"][1]+h["size"])

            self.herbivores.extend(new_herbivores)

            # 3. Lógica Carnívoros
            new_carnivores = []
            for c in self.carnivores[:]:
                # Perseguir herbívoro
                hunt_vec = np.array([0.0, 0.0])
                min_hd = 999
                target_h = None
                for h in self.herbivores:
                    diff, dist = self.get_shortest_dist(c["pos"], h["pos"])
                    if dist < min_hd:
                        min_hd = dist
                        hunt_vec = diff
                        target_h = h
                
                if min_hd < 999:
                    c["pos"] = self.wrap_torus(c["pos"] + (hunt_vec/min_hd)*SPEED_C)
                
                
                # Cazar
                if min_hd < 10 and target_h:
                    c["stomach"] += target_h["energy"]
                    self.canvas.delete(target_h["id"])
                    # CORRECCIÓN: Filtramos la lista usando identidad 'is not' 
                    # para evitar que NumPy intente comparar los arrays de posición
                    self.herbivores = [h for h in self.herbivores if h is not target_h]

                # Metabolismo
                digested = min(c["stomach"], self.digestion_rate.get() * 2)
                c["stomach"] -= digested
                c["energy"] += digested - DECAY_C
                c["age"] += 1

                if c["energy"] > SPLIT_THRESH_C:
                    c["energy"] /= 2
                    new_carnivores.append(self.create_agent("C"))

                if c["energy"] <= 0 or c["age"] > LIFESPAN:
                    self.canvas.delete(c["id"])
                    self.carnivores.remove(c)
                else:
                    self.canvas.coords(c["id"], c["pos"][0]-c["size"], c["pos"][1]-c["size"], 
                                       c["pos"][0]+c["size"], c["pos"][1]+c["size"])
            
            self.carnivores.extend(new_carnivores)

            # 4. Actualizar Interfaz
            self.update_ui_stats()

        self.root.after(20, self.update_loop)

    def update_ui_stats(self):
        h_count = len(self.herbivores)
        c_count = len(self.carnivores)
        self.stats_label.config(text=f"Herbívoros: {h_count}\nCarnívoros: {c_count}\nEnergía Promedio H: {np.mean([h['energy'] for h in self.herbivores]) if h_count>0 else 0:.1f}")
        
        # Actualizar Barras (escaladas)
        self.bar_h.config(width=min(h_count, 200))
        self.bar_c.config(width=min(c_count * 10, 200))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()