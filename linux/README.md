# QuForge Industrial Studio

**QuForge Industrial Studio** is a professional, 10-qubit Quantum Electronic Design Automation (EDA) platform designed for researchers, students, and engineers. It bridges the gap between complex quantum mathematical models and physical circuit design by simulating realistic quantum hardware physics, including noise, decoherence, and connectivity constraints.

---

## 🚀 Introduction

QuForge provides an integrated environment for designing, simulating, analyzing, and optimizing quantum algorithms. Unlike conventional quantum simulators, QuForge emphasizes **Hardware-Aware Quantum Design**, allowing users to model real-world quantum limitations such as:

- \( T_1 \) relaxation (energy decay)
- \( T_2 \) dephasing (loss of phase coherence)
- Electromagnetic Interference (EMI)
- Physical qubit connectivity constraints

This makes QuForge suitable for **industrial-grade quantum workflows**, academic research, and advanced learning.

---

## 🛠️ Key Features

### 🔷 Interactive Design Canvas
- Drag-and-drop quantum EDA grid
- Horizontal lines represent qubits (`Q0`–`Q9`)
- Vertical axis represents time in nanoseconds (ns)

### 🔷 Hardware Simulation
- Configurable \( T_1 \), \( T_2 \), and readout error rates
- Realistic noise and decoherence modeling
- Hardware-constrained execution timing

### 🔷 Industrial Resource Reporting
- Circuit fidelity estimation
- State vector probability analysis
- Top 8 most probable quantum states displayed

### 🔷 Diagnostic Tools
- Crosstalk Map for noise coupling visualization
- EMI Error Detector for pulse collision prevention

### 🔷 Advanced Visualizers
- 3D Bloch Sphere visualization
- Pulse scheduling and timing diagrams
- Coherence maps for entanglement density

### 🔷 Python Scripting Editor
- Built-in Python editor for automation
- Programmatic circuit generation
- Direct access to internal `self.sim` simulation object

---

## 💻 Installation

### 1️⃣ Prerequisites

Ensure your system meets the following requirements:

- Linux OS (Ubuntu recommended)
- Python 3.8 or higher
- pip (Python package manager)
- Tkinter (GUI support)
- Git (version control)

Install prerequisites using:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk git


##2️⃣ Clone the Repository

Clone the QuForge Industrial Studio repository:
