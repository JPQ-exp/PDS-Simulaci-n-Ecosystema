<img width="840" height="650" alt="Simulación de ecosistema" src="https://github.com/user-attachments/assets/912ffe17-4c5c-468d-8299-b7b325beec4d" />
# PDS-Simulaci-n-Ecosystema
Es una simulación de ecosistema viable, con modificacion de parametros en python visualizado en tkinter.
# Axiomatic Persistence: An Emergent Ecosystem Simulation

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Este proyecto es una implementación interactiva de un ecosistema dinámico basado en los principios de **Persistencia Axiomática** y **Sistemas Dinámicos de Persistencia (PDS)**. 

A diferencia de las simulaciones ecológicas tradicionales que imponen límites de población externos (Top-Down), en este modelo la estabilidad y la capacidad de carga (Carrying Capacity) son **propiedades emergentes** que surgen estrictamente de restricciones metabólicas, espaciales y temporales internas (Bottom-Up).

## 🚀 Características Clave

- **Estabilidad Emergente:** El equilibrio entre herbívoros, carnívoros y recursos no está pre-programado. Surge de la interacción entre el decaimiento entrópico y la eficiencia adaptativa.
- **Campos Sensoriales Activos:** Los agentes operan bajo una función de costo que combina atracción hacia el alimento y repulsión (miedo) hacia los depredadores mediante leyes de potencia no lineales.
- **Distancias Temporales Realistas:** Implementación de retardos en la digestión (metabolismo diferido) e inercia cognitiva (delay sensorial), evitando la "tiranía de lo instantáneo".
- **Geometría de Toro:** El espacio de simulación es topológicamente un toro, eliminando los efectos de borde y permitiendo flujos de población continuos.
- **Escalamiento Alométrico:** Diferenciación física y energética entre especies. Los carnívoros son más masivos, poseen mayor inercia metabólica y requieren umbrales de replicación más altos.

## 🧠 Fundamentos Teóricos

El motor de la simulación se basa en dos flujos acoplados:

1.  **Flujo Metabólico ($x$):** Representa la masa de persistencia. Está sujeto a un decaimiento continuo (entropía) y se alimenta mediante un proceso de digestión retardada.
2.  **Flujo de Configuración ($z$):** La dinámica de movimiento en el espacio. Los agentes ajustan su estado interno para minimizar la "sorpresa" o el error respecto a su nicho de viabilidad.

> **Nota:** *Las ecuaciones específicas y el marco formal del modelo matemático subyacente se detallarán en una futura actualización de la documentación.*

## 🛠️ Instalación y Uso

### Requisitos
- Python 3.x
- NumPy

### Ejecución
Clona el repositorio y ejecuta el script principal:
```bash
git clone https://github.com/tu-usuario/axiomatic-persistence.git
cd axiomatic-persistence
python main_gui.py
```

## 🎮 Interfaz de Usuario

La simulación incluye un panel de control en tiempo real (Tkinter) para manipular las constantes universales del ecosistema:

- **Radio de Miedo (Sensor):** Ajusta el alcance del campo de repulsión de los herbívoros.
- **Delay de Comida (Crecimiento):** Controla el tiempo de recuperación de los parches de recursos (la "fricción" del entorno).
- **Tasa de Digestión:** Modifica la velocidad a la que el stock del estómago se convierte en energía vital.

## 📊 Visualización
- **Esferas Cian:** Herbívoros (Adaptación rápida, baja masa).
- **Esferas Rojas:** Carnívoros (Adaptación lenta, alta inercia).
- **Puntos Verdes:** Recursos (Energía potencial disponible).
- **Barras Laterales:** Monitor de población en tiempo real.

---

### Contribuciones
Las ideas sobre cómo extender los retardos temporales o introducir mutaciones en los parámetros metabólicos son bienvenidas. Siéntete libre de abrir un *Issue* o enviar un *Pull Request*.

**Autor:** JPQ-exp  
**Licencia:** MIT
**Zenodo:** http://doi.org/10.5281/zenodo.20054974
