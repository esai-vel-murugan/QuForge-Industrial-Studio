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
```

## 2️⃣ Clone the Repository

Clone the QuForge Industrial Studio repository:
```bash
git clone https://github.com/esai-vel-murugan/QuForge-Industrial-Studio.git
````
Navigate to the Linux directory:
```bash
Copy code
cd QuForge-Industrial-Studio/linux
```

## 3️⃣ Install Python Dependencies
Install required Python libraries:
```bash
pip install numpy matplotlib networkx scipy
```
⚠️ If required, use pip3 instead of pip.

## 4️⃣ Run the Installer Script
Grant execution permission:
```bash
chmod +x install_quforge.sh
```
Run the installer:
```bash
./install_quforge.sh
```
Update the Application Menu:
```bash
update-desktop-database ~/.local/share/applications
```
This step:
- Configures the execution environment
- Creates a desktop shortcut
- Adds QuForge to the application menu

## 5️⃣ Launch QuForge Industrial Studio
Launch using:

- Application Menu → QuForge Industrial Studio

OR via Terminal:
```bash
python3 quforge.py
```
## 📖 How to Use
### 🎛️ Visual Circuit Building
#### Select a Gate
- Choose a quantum gate (H, X, Y, Z, M) from the toolbar.
#### Place a Gate:
- Click on a qubit line (Q0–Q9) at the required time (ns).
#### Create Entanglement
- Click the CNOT button
- Select the control qubit
- Select the target qubit
#### Analyze Results
- Use 3D Bloch Sphere for single-qubit states
- Use Coherence Map for multi-qubit entanglement

## 🧠 Programmatic Design
- Click the PYTHON SCRIPT button
- Write or load .py scripts
- Generate quantum circuits automatically
- Click RUN ALGORITHM to execute
## 🏆 Competitive Analysis: The QuForge Advantage

In the current quantum ecosystem, most tools focus on either pure mathematical theory or heavy programmatic SDKs. **QuForge Industrial Studio** is positioned as a specialized **Engineering Design Tool (EDA)**, bridging the gap between logic and physical hardware constraints.

### **Ecosystem Comparison**

| Feature | **QuForge Studio** | **Qiskit / Cirq** | **Quirk (Web)** |
| :--- | :--- | :--- | :--- |
| **Primary Interface** | **Visual EDA Canvas** | Python Code / SDK | Web Drag-and-Drop |
| **Hardware Modeling** | 10-Qubit Industrial Ring | Generic Cloud Backend | Mathematical Theory |
| **Noise Simulation** | $T_1, T_2$, EMI, & Readout | Manual Code Models | None |
| **Visual Diagnostics** | **Live Bloch & Coherence** | Static Matplotlib Plots | Real-time Math |
| **Collision Alerts** | **Yes (EMI Detection)** | No | No |


### **Why Choose QuForge?**

1. **Design-First Workflow**: Unlike Qiskit or Cirq, which are "code-first," QuForge allows you to build hardware-ready circuits visually. You don't need to write 50 lines of Python just to see how $T_1$ relaxation affects your circuit; simply adjust the **Calibration Sidebar**.
   
2. **Physics-Aware Simulation**: While tools like Quirk are excellent for learning gate logic, they ignore the "physics" of the hardware. QuForge is built for the **Industrial Workflow**, where pulse interference (EMI) and qubit dephasing are critical design factors.

3. **Unique EMI Collision Detection**: QuForge is one of the few open-source visual tools that warns you if your quantum pulses are physically too close in time/space, simulating real-world electromagnetic crosstalk that occurs on superconducting chips.

4. **Low Barrier to Engineering**: QuForge provides a native Linux installer and a dedicated GUI, allowing researchers and students to move from theoretical gates to hardware-constrained engineering in under 5 minutes.

5. **Zero-Code Entry**: You don't need to know PyTorch or complex Python syntax to build a Bell State. Use the drag-and-drop canvas for instant visual feedback on the **Bloch Sphere**.

6. **Hardware-Ready Logic**: Most simulators (including the qudit library) focus on the "State Vector." Our Industrial Studio focuses on the **Hardware Ring**, showing you exactly how physical constraints like pulse collisions affect your fidelity.

# 🏆 Competitive Analysis: The QuForge Advantage

QuForge Industrial Studio occupies a unique niche in the quantum ecosystem, prioritizing hardware-aware engineering over abstract mathematical simulation.

| Feature | **QuForge Industrial Studio** | **QuForge (qudits)** | 
| :--- | :--- | :--- | 
| **Core Focus** | **Visual Hardware EDA** | High-dim Qudits |
| **Primary UI** | **Desktop GUI** | Python API | 
| **Hardware Noise** | **EMI, $T_1$, $T_2$ Sliders** | Planned/Basic | 
| **Backend** | Custom Physics Engine | PyTorch / GPU | 
| **Target User** | **Industrial Engineers** | Research Physicists | 



