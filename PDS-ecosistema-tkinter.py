import tkinter as tk
import numpy as np
import random

# ==========================================
# CONSTANTES ESTRUCTURALES
# ==========================================
WIDTH, HEIGHT = 600, 600
INITIAL_HERBIVORES = 45
INITIAL_CARNIVORES = 7
GRID_SIZE = 15  # Rejilla de 15x15
C_VISION_RADIUS = 180  # Rango de visión FIJO para carnívoros
FPS_DELAY = 33  # ~30 FPS (Equilibrio de rendimiento)

DECAY_H, DECAY_C = 0.05, 0.08
SPEED_H, SPEED_C = 2.6, 3.1
SPLIT_THRESH_H, SPLIT_THRESH_C = 8.0, 25.0
LIFESPAN = 1000 

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ecosistema: Percepción Local y Eficiencia")
        
        self.fear_radius = tk.DoubleVar(value=30.0)
        self.growth_delay = tk.DoubleVar(value=50.0)
        self.digestion_rate = tk.DoubleVar(value=1.0)
        self.is_running = True

        self.setup_ui()
        self.init_simulation_state()
        self.update_loop()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        panel = tk.Frame(main_frame, bg="#2c3e50", width=250)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(panel, text="SISTEMA DE CONTROL", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(pady=10)
        self.create_slider(panel, "Radio Evasión (H)", self.fear_radius, 10, 100)
        self.create_slider(panel, "Regeneración Comida", self.growth_delay, 10, 200)
        self.create_slider(panel, "Tasa Digestiva", self.digestion_rate, 0.1, 2.0)

        self.stats_label = tk.Label(panel, text="", fg="#ecf0f1", bg="#2c3e50", justify=tk.LEFT, font=("Courier", 9))
        self.stats_label.pack(pady=10)

        # Barras de Población
        self.bar_h_container = tk.Frame(panel, bg="#34495e", height=15, width=200)
        self.bar_h_container.pack_propagate(False)
        self.bar_h_container.pack(pady=2)
        self.bar_h = tk.Frame(self.bar_h_container, bg="#3498db", height=15); self.bar_h.place(x=0, y=0, width=0)

        self.bar_c_container = tk.Frame(panel, bg="#34495e", height=15, width=200)
        self.bar_c_container.pack_propagate(False)
        self.bar_c_container.pack(pady=2)
        self.bar_c = tk.Frame(self.bar_c_container, bg="#e74c3c", height=15); self.bar_c.place(x=0, y=0, width=0)

        tk.Button(panel, text="PAUSAR", command=self.toggle_sim, bg="#e67e22", fg="white").pack(pady=10, fill=tk.X, padx=20)
        tk.Button(panel, text="REINICIAR", command=self.reset_simulation, bg="#95a5a6", fg="white").pack(pady=5, fill=tk.X, padx=20)

    def create_slider(self, parent, text, var, low, high):
        tk.Label(parent, text=text, fg="#bdc3c7", bg="#2c3e50", font=("Arial", 8)).pack()
        tk.Scale(parent, from_=low, to=high, orient=tk.HORIZONTAL, variable=var, bg="#2c3e50", fg="white", highlightthickness=0, length=180).pack(pady=2)

    def init_simulation_state(self):
        self.canvas.delete("all")
        self.food_patches = []
        step_x, step_y = WIDTH / GRID_SIZE, HEIGHT / GRID_SIZE

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x, y = (i * step_x) + (step_x / 2), (j * step_y) + (step_y / 2)
                # Alimento inicial disponible (Verde)
                item_id = self.canvas.create_rectangle(x-2, y-2, x+2, y+2, fill="#2ecc71", outline="")
                self.food_patches.append([x, y, 0, item_id])

        self.herbivores = [self.create_agent("H") for _ in range(INITIAL_HERBIVORES)]
        self.carnivores = [self.create_agent("C") for _ in range(INITIAL_CARNIVORES)]

    def create_agent(self, type):
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        color = "#3498db" if type == "H" else "#e74c3c"
        size = 3 if type == "H" else 5
        return {
            "pos": np.array([x, y]), "energy": 5.0 if type == "H" else 18.0,
            "stomach": 0.0, "type": type, "id": self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline=""),
            "age": 0, "size": size, "alive": True
        }

    def toggle_sim(self): self.is_running = not self.is_running
    def reset_simulation(self): self.init_simulation_state(); self.is_running = True
    def wrap_torus(self, pos): return np.mod(pos, [WIDTH, HEIGHT])
    def get_shortest_dist(self, p1, p2):
        delta = p2 - p1
        delta = (delta + [WIDTH/2, HEIGHT/2]) % [WIDTH, HEIGHT] - [WIDTH/2, HEIGHT/2]
        return delta, np.linalg.norm(delta)

    def update_loop(self):
        if self.is_running:
            # 1. Alimento: Ciclo de regeneración
            for f in self.food_patches:
                if f[2] > 0:
                    f[2] -= 1
                    if f[2] <= 0: self.canvas.itemconfig(f[3], fill="#2ecc71")

            # 2. Herbívoros: Lógica de Sensor Avanzada
            new_h = []
            for h in self.herbivores:
                # Evasión de carnívoros (Sensor ajustable)
                evasion_vec = np.array([0.0, 0.0])
                for c in self.carnivores:
                    diff, dist = self.get_shortest_dist(h["pos"], c["pos"])
                    if dist < self.fear_radius.get():
                        evasion_vec -= diff / (dist + 0.1)

                # Búsqueda de COMIDA DISPONIBLE (Optimización de Rejilla)
                food_vec = np.array([0.0, 0.0]); min_fd = 999
                # Solo mira los parches de comida que estén realmente "verdes"
                for f in self.food_patches:
                    if f[2] <= 0: # Axioma: "Solo veo lo que está disponible"
                        diff, dist = self.get_shortest_dist(h["pos"], [f[0], f[1]])
                        if dist < min_fd and dist < 120: # Rango visión H limitado a 120
                            min_fd = dist; food_vec = diff
                
                # Movimiento
                move = (food_vec * 0.18) + (evasion_vec * 2.5)
                norm = np.linalg.norm(move)
                if norm > 0: move = (move / norm) * SPEED_H
                h["pos"] = self.wrap_torus(h["pos"] + move + np.random.normal(0, 0.2, 2))
                
                # Comer (Optimización de proximidad)
                if min_fd < 8:
                    for f in self.food_patches:
                        if f[2] <= 0:
                            _, d = self.get_shortest_dist(h["pos"], [f[0], f[1]])
                            if d < 8:
                                h["stomach"] += 3.5
                                f[2] = self.growth_delay.get()
                                self.canvas.itemconfig(f[3], fill="#1a1a1a")
                                break

                # Metabolismo y muerte
                dig = min(h["stomach"], self.digestion_rate.get())
                h["stomach"] -= dig
                h["energy"] += dig - DECAY_H
                h["age"] += 1
                if h["energy"] > SPLIT_THRESH_H:
                    h["energy"] /= 2.2; new_h.append(self.create_agent("H"))
                if h["energy"] <= 0 or h["age"] > LIFESPAN:
                    h["alive"] = False; self.canvas.delete(h["id"])

            # 3. Carnívoros: Visión Amplia y FIJA
            new_c = []
            for c in self.carnivores:
                hunt_vec = np.array([0.0, 0.0]); min_hd = 999; target_h = None
                
                # Solo ven herbívoros dentro de C_VISION_RADIUS (180px)
                for h in self.herbivores:
                    if not h["alive"]: continue
                    diff, dist = self.get_shortest_dist(c["pos"], h["pos"])
                    if dist < min_hd and dist < C_VISION_RADIUS:
                        min_hd = dist; hunt_vec = diff; target_h = h
                
                if target_h:
                    c["pos"] = self.wrap_torus(c["pos"] + (hunt_vec/(min_hd+0.1))*SPEED_C)
                    if min_hd < 10:
                        c["stomach"] += target_h["energy"]
                        target_h["alive"] = False; self.canvas.delete(target_h["id"])
                else:
                    # Si no ve nada, patrulla aleatoriamente
                    c["pos"] = self.wrap_torus(c["pos"] + np.random.uniform(-2, 2, 2))

                dig = min(c["stomach"], self.digestion_rate.get() * 1.5)
                c["stomach"] -= dig
                c["energy"] += dig - DECAY_C
                c["age"] += 1
                if c["energy"] > SPLIT_THRESH_C:
                    c["energy"] /= 2.2; new_c.append(self.create_agent("C"))
                if c["energy"] <= 0 or c["age"] > LIFESPAN:
                    c["alive"] = False; self.canvas.delete(c["id"])

            # Sincronización
            self.herbivores = [h for h in self.herbivores if h["alive"]]
            self.carnivores = [c for c in self.carnivores if c["alive"]]
            self.herbivores.extend(new_h); self.carnivores.extend(new_c)

            for a in self.herbivores + self.carnivores:
                self.canvas.coords(a["id"], a["pos"][0]-a["size"], a["pos"][1]-a["size"], a["pos"][0]+a["size"], a["pos"][1]+a["size"])

            self.update_ui_stats()

        self.root.after(FPS_DELAY, self.update_loop)

    def update_ui_stats(self):
        h_n, c_n = len(self.herbivores), len(self.carnivores)
        self.stats_label.config(text=f"HERBÍVOROS: {h_n:03d}\nCARNÍVOROS: {c_n:03d}\nVISIÓN C: {C_VISION_RADIUS}px")
        self.bar_h.place_configure(width=min(int(h_n * 2), 200))
        self.bar_c.place_configure(width=min(int(c_n * 2), 200))

if __name__ == "__main__":
    root = tk.Tk(); root.configure(bg="#1a1a1a")
    app = SimulationApp(root); root.mainloop()