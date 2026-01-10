import numpy as np

class QuantumSimulator:
    def __init__(self, qubits=10):
        self.qubits = qubits
        # Industrial Coupling Map (Linear Chain)
        self.coupling_map = {i: [(i-1)%qubits, (i+1)%qubits] for i in range(qubits)}
        self.reset()
        
        self.gates = {
            'H': (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]]),
            'X': np.array([[0, 1], [1, 0]]),
            'Y': np.array([[0, -1j], [1j, 0]]),
            'Z': np.array([[1, 0], [0, -1]]),
            'I': np.eye(2)
        }

    def reset(self):
        self.state = np.zeros(2**self.qubits, dtype=complex)
        self.state[0] = 1.0 
        self.total_leakage = 0.0

    def apply_gate(self, name, target, t1, t2, g_err, apply_crosstalk=True):
        # 1. Calculate Leakage based on fidelity
        fidelity = 1 - (g_err / 100.0)
        self.total_leakage += (1 - fidelity) * 0.1
        
        # 2. Apply Primary Gate
        matrix = self.gates.get(name, self.gates['I'])
        self._evolve(matrix, target)

        # 3. Industrial Feature: Crosstalk
        if apply_crosstalk:
            neighbors = self.coupling_map.get(target, [])
            for neighbor in neighbors:
                theta = 0.02 * np.random.normal() # Strength = 0.02
                rz_stray = np.array([[np.exp(-1j*theta/2), 0], [0, np.exp(1j*theta/2)]])
                self._evolve(rz_stray, neighbor)

        self._apply_decoherence(t1, t2)

    def apply_cnot(self, ctrl, targ, t1, t2, g_err):
        size = 2**self.qubits
        op = np.eye(size, dtype=complex)
        for i in range(size):
            bits = list(bin(i)[2:].zfill(self.qubits))
            if bits[ctrl] == '1':
                bits[targ] = '1' if bits[targ] == '0' else '0'
                target_idx = int("".join(bits), 2)
                op[i, i], op[target_idx, target_idx] = 0, 0
                op[i, target_idx], op[target_idx, i] = 1, 1
        self.state = np.dot(op, self.state)
        self.total_leakage += (g_err / 50.0) * 0.1 # CNOTs leak more
        self._apply_decoherence(t1, t2)

    def _evolve(self, matrix, target):
        op = np.array([1.0])
        for i in range(self.qubits):
            op = np.kron(op, matrix if i == target else np.eye(2))
        self.state = np.dot(op, self.state)

    def _apply_decoherence(self, t1, t2):
        dt = 0.1
        phase_decay = np.exp(-dt / t2)
        relax_decay = np.exp(-dt / t1)
        for i in range(len(self.state)):
            if i > 0: self.state[i] *= phase_decay
        prob_ex = 1 - np.abs(self.state[0])**2
        self.state[0] = np.sqrt(np.abs(self.state[0])**2 + prob_ex * (1 - relax_decay))
        norm = np.linalg.norm(self.state)
        if norm > 0: self.state /= norm

    def get_probabilities(self, readout_err):
        probs = np.abs(self.state)**2
        err = readout_err / 100.0
        return probs * (1 - err) + (err / len(probs))
