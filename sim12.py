import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkFont

# --- Define fiber type parameters (ITU-T Standard Fibers) ---
fiber_types = {
    "G.652D": {
        "attenuation_coeff": 0.20,
        "base_bending_loss": 0.10,
        "ideal_bend_radius": 5.0,
        "MFD": 9.2,
        "A": 0.2, "B": 1.5,
        "description": "Standard Single Mode Fiber (ITU-T G.652D) with attenuation 0.20 dB/km at 1550 nm."
    },
    "G.657A": {
        "attenuation_coeff": 0.18,
        "base_bending_loss": 0.05,
        "ideal_bend_radius": 3.0,
        "MFD": 8.8,
        "A": 0.1, "B": 1.8,
        "description": "Bend Insensitive Fiber (ITU-T G.657A) with lower bending loss."
    },
    "G.655": {
        "attenuation_coeff": 0.22,
        "base_bending_loss": 0.15,
        "ideal_bend_radius": 5.0,
        "MFD": 10.0,
        "A": 0.25, "B": 1.3,
        "description": "Non-Zero Dispersion-Shifted Fiber (ITU-T G.655)."
    }
}

# Global constants
bend_angle = 90.0  # Bend angle in degrees

# --- Simulation functions ---
def marcuse_bending_loss(A, B, R, MFD):
    """Calculate bending loss using Marcuse’s formula."""
    return A * np.exp(-B * (R / MFD))

def empirical_bending_loss(base_loss, ideal_radius, bend_radius, bend_angle_deg):
    """Calculate bending loss using empirical formula."""
    return base_loss * (ideal_radius / bend_radius) * (bend_angle_deg / 90.0)

def simulate_bending_loss(fiber_type, bend_radii, model):
    """Simulate bending loss using Marcuse or Empirical model."""
    params = fiber_types[fiber_type]
    A, B, MFD = params["A"], params["B"], params["MFD"]
    base_loss = params["base_bending_loss"]
    ideal_radius = params["ideal_bend_radius"]

    losses = []
    for R in bend_radii:
        if model == "Marcuse":
            loss = marcuse_bending_loss(A, B, R, MFD)
        else:
            loss = empirical_bending_loss(base_loss, ideal_radius, R, bend_angle)
        losses.append(loss)

    return losses

# --- GUI Functions ---
def update_fiber_description(*args):
    fiber_type = fiber_type_var.get()
    description = fiber_types[fiber_type]["description"]
    fiber_desc_label.config(text=f"Fiber Type: {fiber_type}\n{description}")

def run_bending_simulation():
    """Run bending loss simulation for selected fiber and model."""
    fiber_type = fiber_type_var.get()
    model = model_var.get()

    try:
        bend_from = float(bend_from_entry.get())
        bend_to = float(bend_to_entry.get())
    except ValueError:
        result_label.config(text="Enter valid bending radius range values (cm).")
        return

    bend_radii = np.linspace(bend_from, bend_to, 100)
    loss_values = simulate_bending_loss(fiber_type, bend_radii, model)

    # Update graph
    ax_bending.clear()
    ax_bending.plot(bend_radii, loss_values, label=f"{model} Model Loss", color="green")
    ax_bending.set_xlabel("Bending Radius (cm)")
    ax_bending.set_ylabel("Bending Loss (dB/km)")
    ax_bending.set_title(f"Bending Loss vs Radius ({fiber_type})")
    ax_bending.legend()
    ax_bending.grid()
    canvas_bending.draw()

    result_label.config(text=f"[Bending Sim] At R = {bend_radii[-1]:.2f} cm: Loss ≈ {loss_values[-1]:.2f} dB/km")

# --- GUI Setup ---
root = tk.Tk()
root.title("Optical Fiber Bending Loss Simulation")

fiber_type_var = tk.StringVar(value="G.652D")
model_var = tk.StringVar(value="Marcuse")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0)

# Fiber type selection
ttk.Label(frame, text="Select Fiber Type:").grid(row=0, column=0)
fiber_menu = ttk.Combobox(frame, textvariable=fiber_type_var, values=list(fiber_types.keys()), state="readonly")
fiber_menu.grid(row=0, column=1)
fiber_type_var.trace("w", update_fiber_description)

# Model selection (Marcuse or Empirical)
ttk.Label(frame, text="Select Loss Model:").grid(row=1, column=0)
model_menu = ttk.Combobox(frame, textvariable=model_var, values=["Marcuse", "Empirical"], state="readonly")
model_menu.grid(row=1, column=1)

# Bending radius input
ttk.Label(frame, text="Bend Radius Range (cm):").grid(row=2, column=0)
bend_from_entry = ttk.Entry(frame, width=5)
bend_from_entry.insert(0, "2")
bend_from_entry.grid(row=2, column=1)

ttk.Label(frame, text="to").grid(row=2, column=2)
bend_to_entry = ttk.Entry(frame, width=5)
bend_to_entry.insert(0, "10")
bend_to_entry.grid(row=2, column=3)

# Run simulation button
ttk.Button(frame, text="Run Bending Simulation", command=run_bending_simulation).grid(row=3, column=0, columnspan=4, pady=10)

# Result label
result_label = ttk.Label(root, text="Results will be shown here.", padding="10")
result_label.grid(row=2, column=0, sticky="W")

# --- Graph Setup ---
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, padx=10, pady=10)

tab_bending = ttk.Frame(notebook)
notebook.add(tab_bending, text="Bending Simulation")

fig_bending, ax_bending = plt.subplots(figsize=(5, 4))
canvas_bending = FigureCanvasTkAgg(fig_bending, master=tab_bending)
canvas_bending.get_tk_widget().pack(fill="both", expand=True)

root.mainloop()
