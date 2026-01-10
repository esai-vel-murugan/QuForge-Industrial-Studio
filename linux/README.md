# VLSI: Basic Concepts and Integrated Circuits

This repository contains notes and summaries based on the "Basic Concepts of Integrated Circuits" lecture series.

---

## 1. Historical Perspective & Moore's Law
The transition from discrete electronic circuits to **Integrated Circuits (ICs)** revolutionized technology by making electronics cheaper, faster, and more reliable.

* **Miniaturization:** Scaling down transistor sizes (e.g., 90nm → 45nm → 16nm).
* **Moore's Law:** The number of components in an IC, realized at minimum cost, doubles approximately every two years.
* **Benefits:**
    * Increased Speed
    * Improved Energy Efficiency
    * Lower cost per transistor

---

## 2. Structure of an Integrated Circuit
Modern ICs are built in a 3D layered architecture.

* **Bottom Layer:** Active devices (Transistors like PMOS and NMOS).
* **Interconnect Layers:** Multiple layers of metal (Metal-1, Metal-2, etc.) separated by dielectrics.
* **Vias:** Conductive "tunnels" used to make electrical connections between different metal layers.



---

## 3. The Fabrication Process: Photolithography
Photolithography is the crux of IC manufacturing. It is the process of transferring geometric shapes from a **mask** to a silicon wafer.

### Steps in Photolithography:
1.  **Film Deposition:** Placing a thin layer of material on the substrate.
2.  **Photoresist Application:** Coating the surface with light-sensitive material.
3.  **Exposure:** Using UV light and a mask to define the pattern.
4.  **Development:** Removing the exposed/unexposed photoresist.
5.  **Etching:** Chemically removing the undesired material.
6.  **Photoresist Removal:** Final cleaning to leave only the patterned film.

---

## 4. Hardware Definitions
It is essential to distinguish between the different stages of the physical hardware:

| Term | Description |
| :--- | :--- |
| **Silicon Ingot** | A massive cylindrical single crystal of silicon. |
| **Silicon Wafer** | A thin slice of silicon (e.g., 300mm) used as a substrate. |
| **Die** | A single rectangular circuit sliced out of a wafer. |
| **Chip** | A packaged die encapsulated for physical and chemical protection. |



---

## 5. Semiconductor Industry Business Models
The industry is divided based on whether a company designs, manufactures, or does both.

* **Fabless Design:** Companies that only design chips and outsource fabrication (e.g., **Nvidia, Qualcomm**).
* **Merchant Foundries:** Companies that only manufacture chips for others (e.g., **TSMC, GF**).
* **IDM (Integrated Device Manufacturers):** Companies that handle both design and fabrication (e.g., **Intel, Samsung**).

---
*Notes based on NPTEL VLSI Lecture Series.*
