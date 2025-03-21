import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog

# --- Define fiber type parameters based on ITU-T standards ---
fiber_types = {
    "G.652D": {
        "attenuation_coeff": 0.20,
        "base_bending_loss": 0.10,
        "ideal_bend_radius": 5.0,
        "description": "Standard Single Mode Fiber (ITU-T G.652D) with typical attenuation 0.20 dB/km at 1550 nm."
    },
    "G.657A": {
        "attenuation_coeff": 0.18,
        "base_bending_loss": 0.05,
        "ideal_bend_radius": 3.0,
        "description": "Bend Insensitive Fiber (ITU-T G.657A) with improved bending loss and lower attenuation."
    },
    "G.655": {
        "attenuation_coeff": 0.22,
        "base_bending_loss": 0.15,
        "ideal_bend_radius": 5.0,
        "description": "Non-Zero Dispersion-Shifted Fiber (ITU-T G.655) with slightly higher attenuation."
    }
}

# Global simulation constants
I_in = 1000.0         # Input current in µA
number_of_bends = 5   # Number of bends along fiber length
bend_angle = 90.0     # Bend angle in degrees
room_temperature = 25.0   # Reference temperature in °C
temp_coefficient = 0.0002 # Temperature loss coefficient (dB/km/°C)
noise_std = 0.02          # Noise standard deviation (fraction of I_out)

# --- Simulation functions ---
def calculate_numerical_aperture(D, b):
    theta = np.arctan(D / (2 * b))  # in radians
    NA = np.sin(theta)
    theta_deg = np.degrees(theta)
    return theta_deg, NA

def bending_loss(baseline, ideal, bend_radius, bend_angle_deg):
    # Loss scales inversely with bend radius compared to ideal value, normalized to 90°
    return baseline * (ideal / bend_radius) * (bend_angle_deg / 90.0)

def simulate_output_current(fiber_length, bend_radius, ambient_temp, attenuation_coeff, base_bending_loss, ideal_bend_radius):
    # Calculate deterministic losses over the fiber length (in dB)
    loss_attenuation = attenuation_coeff * fiber_length
    loss_temp = temp_coefficient * abs(ambient_temp - room_temperature) * fiber_length
    # Bending loss: loss per bend times the number of bends
    loss_per_bend = bending_loss(base_bending_loss, ideal_bend_radius, bend_radius, bend_angle)
    total_bending_loss = number_of_bends * loss_per_bend
    total_loss = loss_attenuation + total_bending_loss + loss_temp  # Total loss in dB
    # Convert total loss (dB) to output current (µA)
    I_out = I_in * 10 ** (-total_loss / 10)
    # Add random noise to simulate measurement variability
    noise = np.random.normal(0, noise_std * I_out)
    return I_out + noise, total_loss

# --- GUI functions ---
def update_fiber_description(*args):
    # Update the displayed description of the selected fiber type.
    fiber_type = fiber_type_var.get()
    description = fiber_types[fiber_type]["description"]
    fiber_desc_label.config(text=f"Fiber Type: {fiber_type}\n{description}")

def run_length_simulation():
    # Retrieve inputs for fiber length simulation
    fiber_type = fiber_type_var.get()
    try:
        length_start = float(length_start_entry.get())
        length_end = float(length_end_entry.get())
    except ValueError:
        result_label.config(text="Enter valid fiber length values (km).")
        return
    try:
        ambient_temp = float(temp_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid ambient temperature (°C).")
        return
    try:
        bend_radius = float(bend_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid bending radius (cm).")
        return

    params = fiber_types[fiber_type]
    att_coeff = params["attenuation_coeff"]
    base_bend_loss = params["base_bending_loss"]
    ideal_bend_rad = params["ideal_bend_radius"]

    # Simulate over fiber lengths
    fiber_lengths = np.linspace(length_start, length_end, 100)
    output_currents = []
    total_losses = []
    for L in fiber_lengths:
        I_out, tot_loss = simulate_output_current(L, bend_radius, ambient_temp, att_coeff, base_bend_loss, ideal_bend_rad)
        output_currents.append(I_out)
        total_losses.append(tot_loss)

    # Update the top subplot (ax1) with fiber length simulation results
    ax1.clear()
    ax1.plot(fiber_lengths, output_currents, label="Output Current (µA)")
    ax1.set_xlabel("Fiber Length (km)")
    ax1.set_ylabel("Output Current (µA)")
    ax1.set_title(f"Output Current vs Fiber Length ({fiber_type})")
    ax1.grid(True)
    ax1.legend()
    canvas.draw()

    result_label.config(text=f"[Length Sim] At {fiber_lengths[-1]:.2f} km: I_out ≈ {output_currents[-1]:.2f} µA, Loss ≈ {total_losses[-1]:.2f} dB")

def run_bending_simulation():
    # Retrieve inputs for bending simulation
    fiber_type = fiber_type_var.get()
    try:
        fixed_length = float(fixed_length_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid fixed fiber length (km) for bending simulation.")
        return
    try:
        bend_from = float(bend_from_entry.get())
        bend_to = float(bend_to_entry.get())
    except ValueError:
        result_label.config(text="Enter valid bending radius range values (cm).")
        return
    try:
        ambient_temp = float(temp_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid ambient temperature (°C).")
        return

    params = fiber_types[fiber_type]
    att_coeff = params["attenuation_coeff"]
    base_bend_loss = params["base_bending_loss"]
    ideal_bend_rad = params["ideal_bend_radius"]

    # Simulate over a range of bending radii
    bend_radii = np.linspace(bend_from, bend_to, 100)
    output_currents = []
    total_losses = []
    for R in bend_radii:
        I_out, tot_loss = simulate_output_current(fixed_length, R, ambient_temp, att_coeff, base_bend_loss, ideal_bend_rad)
        output_currents.append(I_out)
        total_losses.append(tot_loss)

    # Update the bottom subplot (ax2) with bending simulation results
    ax2.clear()
    ax2.plot(bend_radii, output_currents, color="green", label="Output Current (µA)")
    ax2.set_xlabel("Bending Radius (cm)")
    ax2.set_ylabel("Output Current (µA)")
    ax2.set_title(f"Output Current vs Bending Radius (Fixed Length = {fixed_length} km, {fiber_type})")
    ax2.grid(True)
    ax2.legend()
    canvas.draw()

    result_label.config(text=f"[Bending Sim] At Bend Radius = {bend_radii[-1]:.2f} cm: I_out ≈ {output_currents[-1]:.2f} µA, Loss ≈ {total_losses[-1]:.2f} dB")

def save_graph():
    # Let the user choose where to save the combined figure (both subplots)
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                             title="Save Graph As")
    if file_path:
        fig.savefig(file_path)
        result_label.config(text=f"Graph saved as: {file_path}")

# --- Create the GUI ---
root = tk.Tk()
root.title("G.A.M.B.L.E. Fiber Loss Simulator")

# Input frame
input_frame = ttk.Frame(root, padding="10")
input_frame.grid(row=0, column=0, sticky="W")

# Fiber type selection
ttk.Label(input_frame, text="Select Fiber Type:").grid(row=0, column=0, sticky="W")
fiber_type_var = tk.StringVar(value="G.652D")
fiber_type_menu = ttk.Combobox(input_frame, textvariable=fiber_type_var, values=list(fiber_types.keys()), state="readonly", width=10)
fiber_type_menu.grid(row=0, column=1, sticky="W")
fiber_type_var.trace("w", update_fiber_description)

# Display fiber description
fiber_desc_label = ttk.Label(input_frame, text="", wraplength=300)
fiber_desc_label.grid(row=1, column=0, columnspan=4, pady=(5, 10))
update_fiber_description()  # Initialize description

# Fiber Length Simulation inputs
ttk.Label(input_frame, text="Fiber Length Range (km):").grid(row=2, column=0, sticky="W")
length_start_entry = ttk.Entry(input_frame, width=5)
length_start_entry.insert(0, "0.1")
length_start_entry.grid(row=2, column=1, sticky="W")
ttk.Label(input_frame, text="to").grid(row=2, column=2, sticky="W")
length_end_entry = ttk.Entry(input_frame, width=5)
length_end_entry.insert(0, "10")
length_end_entry.grid(row=2, column=3, sticky="W")

# Ambient temperature input (used for both simulations)
ttk.Label(input_frame, text="Ambient Temperature (°C):").grid(row=3, column=0, sticky="W")
temp_entry = ttk.Entry(input_frame, width=5)
temp_entry.insert(0, "30")
temp_entry.grid(row=3, column=1, sticky="W")

# Bending simulation common parameter: bending radius for length simulation
ttk.Label(input_frame, text="Bending Radius (cm) [for Length Sim]:").grid(row=4, column=0, sticky="W")
bend_entry = ttk.Entry(input_frame, width=5)
bend_entry.insert(0, "3")
bend_entry.grid(row=4, column=1, sticky="W")

# Fixed fiber length for bending simulation
ttk.Label(input_frame, text="Fixed Fiber Length for Bending Sim (km):").grid(row=5, column=0, sticky="W")
fixed_length_entry = ttk.Entry(input_frame, width=5)
fixed_length_entry.insert(0, "5")
fixed_length_entry.grid(row=5, column=1, sticky="W")

# Bending radius range for bending simulation
ttk.Label(input_frame, text="Bending Radius Range (cm): From").grid(row=6, column=0, sticky="W")
bend_from_entry = ttk.Entry(input_frame, width=5)
bend_from_entry.insert(0, "2")
bend_from_entry.grid(row=6, column=1, sticky="W")
ttk.Label(input_frame, text="To").grid(row=6, column=2, sticky="W")
bend_to_entry = ttk.Entry(input_frame, width=5)
bend_to_entry.insert(0, "10")
bend_to_entry.grid(row=6, column=3, sticky="W")

# Simulation buttons
simulate_length_button = ttk.Button(input_frame, text="Run Length Simulation", command=run_length_simulation)
simulate_length_button.grid(row=7, column=0, columnspan=2, pady=10)
simulate_bending_button = ttk.Button(input_frame, text="Run Bending Simulation", command=run_bending_simulation)
simulate_bending_button.grid(row=7, column=2, columnspan=2, pady=10)
save_button = ttk.Button(input_frame, text="Save Graph", command=save_graph)
save_button.grid(row=8, column=0, columnspan=4, pady=10)

# Result label for messages
result_label = ttk.Label(root, text="Results will be shown here.", padding="10")
result_label.grid(row=1, column=0, sticky="W")

# Create a matplotlib figure with two subplots (one for each simulation)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
fig.tight_layout(pad=3)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, rowspan=3, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
