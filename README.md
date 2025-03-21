# G.A.M.B.L.E.
### General Algorithm for Measuring Bends, Losses, & Errors

![GAMBLE Logo](https://via.placeholder.com/800x200?text=G.A.M.B.L.E.)

## 🎲 What is G.A.M.B.L.E.?
G.A.M.B.L.E. is a **fiber optics simulation tool** designed to estimate **bending loss, attenuation, and temperature effects** on different fiber types. Whether your experiment flopped or you just enjoy living on the edge of science, this simulator is here to **roll the dice** for you.

## 🚀 Features
- **Simulates total fiber loss** based on bending, length, and temperature.
- **Supports multiple fiber types** (G.652D, G.657A, G.655, G.652C, G.657B).
- **Real-time graphical output** with Matplotlib.
- **User-friendly GUI** powered by Tkinter.
- **Saves graphs** for further analysis.

## 🔧 Installation
To run G.A.M.B.L.E., you need Python **3.8+** and the following dependencies:

```bash
pip install numpy matplotlib tkinter
```

Then, simply clone the repo:
```bash
git clone https://github.com/navaneethred/opticfibresimulation.git
cd opticfibresimulation
python sim11.py
```

## 🕹️ How to Use
1. Select a **fiber type** from the dropdown.
2. Set parameters for **length, temperature, and bending radius**.
3. Click **Run Simulation** for Length, Bending, or Turns.
4. View and save the **loss graphs**.

## 📊 Fiber Types Supported
| Fiber Type | Attenuation Coeff (dB/km) | Base Bending Loss (dB) | Ideal Bend Radius (cm) |
|------------|-------------------------|----------------------|---------------------|
| G.652D     | 0.20                    | 0.10                 | 5.0                 |
| G.657A     | 0.18                    | 0.05                 | 3.0                 |
| G.655      | 0.22                    | 0.15                 | 5.0                 |
| G.652C     | 0.22                    | 0.12                 | 5.0                 |
| G.657B     | 0.18                    | 0.03                 | 2.5                 |

## 🛠️ Future Improvements
- Implement **Monte Carlo simulations** (because it’s called G.A.M.B.L.E. for a reason 🎲)
- Add **multi-core fiber support**

## 🤝 Contributing
Feel free to **fork** this repo, make improvements, and submit a PR!

## 📜 License
MIT License © 2025 Navaneeth Krishna K

---
Remember: **Science is just a fancy way of rolling the dice!** 🎲🔥