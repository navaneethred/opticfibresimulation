import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

# --- Define fiber type parameters based on ITU-T standards ---
fiber_types = {
    "G.652D": {"attenuation_coeff": 0.20, "base_bending_loss": 0.10, "ideal_bend_radius": 5.0},
    "G.657A": {"attenuation_coeff": 0.18, "base_bending_loss": 0.05, "ideal_bend_radius": 3.0},
    "G.655":  {"attenuation_coeff": 0.22, "base_bending_loss": 0.15, "ideal_bend_radius": 5.0}
}

# Default simulation parameters
I_in = 1000.0         # Input current in µA
number_of_bends = 5   # Fixed number of bends
bend_angle = 90.0     # Bend angle in degrees
room_temperature = 25.0   # Reference temperature (°C)
temp_coefficient = 0.0002 # Temperature loss coefficient (dB/km/°C)
noise_std = 0.02          # Noise standard deviation (fraction of I_out)

# --- Simulation functions ---
def calculate_numerical_aperture(D, b):
    theta = np.arctan(D / (2 * b))  # radians
    NA = np.sin(theta)
    theta_deg = np.degrees(theta)
    return theta_deg, NA

def bending_loss(baseline, ideal, bend_radius, bend_angle_deg):
    # Scale loss inversely with bend radius compared to the ideal value.
    return baseline * (ideal / bend_radius) * (bend_angle_deg / 90.0)

def simulate_output_current(fiber_length, bend_radius, ambient_temp, attenuation_coeff, base_bending_loss, ideal_bend_radius):
    # Attenuation loss over fiber length (dB)
    loss_attenuation = attenuation_coeff * fiber_length
    # Temperature-induced loss (dB)
    loss_temp = temp_coefficient * abs(ambient_temp - room_temperature) * fiber_length
    # Bending loss: loss per bend times number of bends
    loss_per_bend = bending_loss(base_bending_loss, ideal_bend_radius, bend_radius, bend_angle)
    total_bending_loss = number_of_bends * loss_per_bend
    # Total loss (dB)
    total_loss = loss_attenuation + total_bending_loss + loss_temp
    # Convert dB loss to output current (µA)
    I_out = I_in * 10 ** (-total_loss / 10)
    # Add measurement noise
    noise = np.random.normal(0, noise_std * I_out)
    return I_out + noise, total_loss

# --- GUI functions ---
def run_simulation():
    # Get GUI inputs
    fiber_type = fiber_type_var.get()
    try:
        length_start = float(length_start_entry.get())
        length_end = float(length_end_entry.get())
    except ValueError:
        result_label.config(text="Please enter valid fiber length values (km).")
        return
    try:
        ambient_temp = float(temp_entry.get())
    except ValueError:
        result_label.config(text="Please enter a valid temperature.")
        return
    try:
        bend_radius = float(bend_entry.get())
    except ValueError:
        result_label.config(text="Please enter a valid bending radius (cm).")
        return

    # Get fiber parameters for the selected type
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

    # Clear previous plot (if any) and plot new simulation result
    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(fiber_lengths, output_currents, label="Output Current (µA)")
    ax.set_xlabel("Fiber Length (km)")
    ax.set_ylabel("Output Current (µA)")
    ax.set_title(f"Output Current vs Fiber Length ({fiber_type})")
    ax.grid(True)
    ax.legend()
    canvas.draw()

    # Update result label with the final output current and total loss at the maximum length.
    result_label.config(text=f"At {fiber_lengths[-1]:.2f} km: I_out ≈ {output_currents[-1]:.2f} µA, Total Loss ≈ {total_losses[-1]:.2f} dB")

# --- Create the GUI ---
root = tk.Tk()
root.title("Optical Fiber Simulation")

# Create a frame for inputs
input_frame = ttk.Frame(root, padding="10")
input_frame.grid(row=0, column=0, sticky="W")

# Fiber type selection
ttk.Label(input_frame, text="Select Fiber Type:").grid(row=0, column=0, sticky="W")
fiber_type_var = tk.StringVar(value="G.652D")
fiber_type_menu = ttk.Combobox(input_frame, textvariable=fiber_type_var, values=list(fiber_types.keys()), state="readonly", width=10)
fiber_type_menu.grid(row=0, column=1, sticky="W")

# Fiber length range entries
ttk.Label(input_frame, text="Fiber Length Range (km):").grid(row=1, column=0, sticky="W")
length_start_entry = ttk.Entry(input_frame, width=5)
length_start_entry.insert(0, "0.1")
length_start_entry.grid(row=1, column=1, sticky="W")
ttk.Label(input_frame, text="to").grid(row=1, column=2, sticky="W")
length_end_entry = ttk.Entry(input_frame, width=5)
length_end_entry.insert(0, "10")
length_end_entry.grid(row=1, column=3, sticky="W")

# Ambient temperature entry
ttk.Label(input_frame, text="Ambient Temperature (°C):").grid(row=2, column=0, sticky="W")
temp_entry = ttk.Entry(input_frame, width=5)
temp_entry.insert(0, "30")
temp_entry.grid(row=2, column=1, sticky="W")

# Bending radius entry
ttk.Label(input_frame, text="Bending Radius (cm):").grid(row=3, column=0, sticky="W")
bend_entry = ttk.Entry(input_frame, width=5)
bend_entry.insert(0, "3")
bend_entry.grid(row=3, column=1, sticky="W")

# Run Simulation button
simulate_button = ttk.Button(input_frame, text="Run Simulation", command=run_simulation)
simulate_button.grid(row=4, column=0, columnspan=2, pady=10)

# Result label to show final output values
result_label = ttk.Label(root, text="Results will be shown here.", padding="10")
result_label.grid(row=1, column=0)

# Create a matplotlib figure for plotting
fig = plt.Figure(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, rowspan=3, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
