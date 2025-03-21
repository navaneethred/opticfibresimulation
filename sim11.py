import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkFont

# --- Define fiber type parameters (5 fiber types) ---
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
    },
    "G.652C": {
        "attenuation_coeff": 0.22,
        "base_bending_loss": 0.12,
        "ideal_bend_radius": 5.0,
        "description": "Legacy Standard Single Mode Fiber (ITU-T G.652C) with slightly higher loss and bending sensitivity."
    },
    "G.657B": {
        "attenuation_coeff": 0.18,
        "base_bending_loss": 0.03,
        "ideal_bend_radius": 2.5,
        "description": "Ultra Bend Insensitive Fiber (ITU-T G.657B) with extremely low bending loss."
    }
}

# Global simulation constants
I_in = 1000.0         # (Reference) Input current in µA (not used directly now)
default_turns = 5     # Default number of turns
bend_angle = 90.0     # Bend angle in degrees
room_temperature = 25.0   # Reference temperature (°C)
temp_coefficient = 0.0002 # Temperature loss coefficient (dB/km/°C)
noise_std = 0.02          # Noise standard deviation (fraction)

# Global storage for simulation data (for saving individual graphs)
length_sim_data = None
bending_sim_data = None
turns_sim_data = None

# --- Simulation functions ---
def calculate_numerical_aperture(D, b):
    theta = np.arctan(D / (2 * b))
    NA = np.sin(theta)
    theta_deg = np.degrees(theta)
    return theta_deg, NA

def bending_loss(baseline, ideal, bend_radius, bend_angle_deg):
    return baseline * (ideal / bend_radius) * (bend_angle_deg / 90.0)

def simulate_total_loss(fiber_length, bend_radius, ambient_temp,
                        attenuation_coeff, base_bending_loss, ideal_bend_radius, n_turns=default_turns):
    # Attenuation loss (dB)
    loss_attenuation = attenuation_coeff * fiber_length
    # Temperature-induced loss (dB)
    loss_temp = temp_coefficient * abs(ambient_temp - room_temperature) * fiber_length
    # Bending loss: loss per bend * number of turns
    loss_per_bend = bending_loss(base_bending_loss, ideal_bend_radius, bend_radius, bend_angle)
    total_bending_loss = n_turns * loss_per_bend
    total_loss = loss_attenuation + total_bending_loss + loss_temp
    # Add random noise to simulate measurement variability
    noise = np.random.normal(0, noise_std * total_loss)
    return total_loss + noise

# --- GUI functions ---
def update_fiber_description(*args):
    fiber_type = fiber_type_var.get()
    description = fiber_types[fiber_type]["description"]
    fiber_desc_label.config(text=f"Fiber Type: {fiber_type}\n{description}")

def run_length_simulation():
    global length_sim_data
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
        result_label.config(text="Enter a valid bending radius (cm) for length sim.")
        return

    params = fiber_types[fiber_type]
    att_coeff = params["attenuation_coeff"]
    base_bend_loss = params["base_bending_loss"]
    ideal_bend_rad = params["ideal_bend_radius"]

    fiber_lengths = np.linspace(length_start, length_end, 100)
    loss_values = []
    for L in fiber_lengths:
        loss = simulate_total_loss(L, bend_radius, ambient_temp,
                                   att_coeff, base_bend_loss, ideal_bend_rad)
        loss_values.append(loss)

    length_sim_data = (fiber_lengths, loss_values)

    ax_length.clear()
    ax_length.plot(fiber_lengths, loss_values, label="Total Loss (dB)")
    ax_length.set_xlabel("Fiber Length (km)")
    ax_length.set_ylabel("Loss (dB)")
    ax_length.set_title(f"Total Loss vs Fiber Length ({fiber_type})")
    ax_length.grid(True)
    ax_length.legend()
    canvas_length.draw()

    result_label.config(text=f"[Length Sim] At {fiber_lengths[-1]:.2f} km: Loss ≈ {loss_values[-1]:.2f} dB")

def run_bending_simulation():
    global bending_sim_data
    fiber_type = fiber_type_var.get()
    try:
        fixed_length = float(fixed_length_bending_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid fixed fiber length (km) for bending sim.")
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

    bend_radii = np.linspace(bend_from, bend_to, 100)
    loss_values = []
    for R in bend_radii:
        loss = simulate_total_loss(fixed_length, R, ambient_temp,
                                   att_coeff, base_bend_loss, ideal_bend_rad)
        loss_values.append(loss)

    bending_sim_data = (bend_radii, loss_values)

    ax_bending.clear()
    ax_bending.plot(bend_radii, loss_values, color="green", label="Total Loss (dB)")
    ax_bending.set_xlabel("Bending Radius (cm)")
    ax_bending.set_ylabel("Loss (dB)")
    ax_bending.set_title(f"Total Loss vs Bending Radius (Fixed Length = {fixed_length} km, {fiber_type})")
    ax_bending.grid(True)
    ax_bending.legend()
    canvas_bending.draw()

    result_label.config(text=f"[Bending Sim] At R = {bend_radii[-1]:.2f} cm: Loss ≈ {loss_values[-1]:.2f} dB")

def run_turns_simulation():
    global turns_sim_data
    fiber_type = fiber_type_var.get()
    try:
        fixed_length = float(fixed_length_turns_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid fixed fiber length (km) for turns sim.")
        return
    try:
        turn_from = int(turn_from_entry.get())
        turn_to = int(turn_to_entry.get())
    except ValueError:
        result_label.config(text="Enter valid turn range values (integer).")
        return
    try:
        bend_radius = float(bend_turns_entry.get())
    except ValueError:
        result_label.config(text="Enter a valid bending radius (cm) for turns sim.")
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

    n_turns_array = np.arange(turn_from, turn_to + 1)
    loss_values = []
    for n in n_turns_array:
        loss = simulate_total_loss(fixed_length, bend_radius, ambient_temp,
                                   att_coeff, base_bend_loss, ideal_bend_rad, n_turns=n)
        loss_values.append(loss)

    turns_sim_data = (n_turns_array, loss_values)

    ax_turns.clear()
    ax_turns.plot(n_turns_array, loss_values, color="red", label="Total Loss (dB)")
    ax_turns.set_xlabel("Number of Turns")
    ax_turns.set_ylabel("Loss (dB)")
    ax_turns.set_title(f"Total Loss vs Number of Turns ({fiber_type})")
    ax_turns.grid(True)
    ax_turns.legend()
    canvas_turns.draw()

    result_label.config(text=f"[Turns Sim] At {n_turns_array[-1]} turns: Loss ≈ {loss_values[-1]:.2f} dB")

# --- Saving functions ---
def save_length_graph():
    if length_sim_data is None:
        result_label.config(text="Run Length Simulation first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                             title="Save Length Simulation Graph As")
    if file_path:
        fig_temp, ax_temp = plt.subplots(figsize=(6,4))
        fiber_lengths, loss_values = length_sim_data
        ax_temp.plot(fiber_lengths, loss_values, label="Total Loss (dB)")
        ax_temp.set_xlabel("Fiber Length (km)")
        ax_temp.set_ylabel("Loss (dB)")
        ax_temp.set_title(f"Total Loss vs Fiber Length ({fiber_type_var.get()})")
        ax_temp.grid(True)
        ax_temp.legend()
        fig_temp.savefig(file_path)
        plt.close(fig_temp)
        result_label.config(text=f"Length graph saved as: {file_path}")

def save_bending_graph():
    if bending_sim_data is None:
        result_label.config(text="Run Bending Simulation first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                             title="Save Bending Simulation Graph As")
    if file_path:
        fig_temp, ax_temp = plt.subplots(figsize=(6,4))
        bend_radii, loss_values = bending_sim_data
        ax_temp.plot(bend_radii, loss_values, color="green", label="Total Loss (dB)")
        ax_temp.set_xlabel("Bending Radius (cm)")
        ax_temp.set_ylabel("Loss (dB)")
        ax_temp.set_title(f"Total Loss vs Bending Radius ({fiber_type_var.get()})")
        ax_temp.grid(True)
        ax_temp.legend()
        fig_temp.savefig(file_path)
        plt.close(fig_temp)
        result_label.config(text=f"Bending graph saved as: {file_path}")

def save_turns_graph():
    if turns_sim_data is None:
        result_label.config(text="Run Turns Simulation first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                             title="Save Turns Simulation Graph As")
    if file_path:
        fig_temp, ax_temp = plt.subplots(figsize=(6,4))
        n_turns_array, loss_values = turns_sim_data
        ax_temp.plot(n_turns_array, loss_values, color="red", label="Total Loss (dB)")
        ax_temp.set_xlabel("Number of Turns")
        ax_temp.set_ylabel("Loss (dB)")
        ax_temp.set_title(f"Total Loss vs Number of Turns ({fiber_type_var.get()})")
        ax_temp.grid(True)
        ax_temp.legend()
        fig_temp.savefig(file_path)
        plt.close(fig_temp)
        result_label.config(text=f"Turns graph saved as: {file_path}")

def save_entire_graph():
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                             title="Save Entire Figure As")
    if file_path:
        fig_entire, (ax_entire1, ax_entire2, ax_entire3) = plt.subplots(3, 1, figsize=(6, 12))
        if length_sim_data is not None:
            fiber_lengths, loss_values = length_sim_data
            ax_entire1.plot(fiber_lengths, loss_values, label="Total Loss (dB)")
            ax_entire1.set_xlabel("Fiber Length (km)")
            ax_entire1.set_ylabel("Loss (dB)")
            ax_entire1.set_title(f"Total Loss vs Fiber Length ({fiber_type_var.get()})")
            ax_entire1.grid(True)
            ax_entire1.legend()
        if bending_sim_data is not None:
            bend_radii, loss_values = bending_sim_data
            ax_entire2.plot(bend_radii, loss_values, color="green", label="Total Loss (dB)")
            ax_entire2.set_xlabel("Bending Radius (cm)")
            ax_entire2.set_ylabel("Loss (dB)")
            ax_entire2.set_title(f"Total Loss vs Bending Radius ({fiber_type_var.get()})")
            ax_entire2.grid(True)
            ax_entire2.legend()
        if turns_sim_data is not None:
            n_turns_array, loss_values = turns_sim_data
            ax_entire3.plot(n_turns_array, loss_values, color="red", label="Total Loss (dB)")
            ax_entire3.set_xlabel("Number of Turns")
            ax_entire3.set_ylabel("Loss (dB)")
            ax_entire3.set_title(f"Total Loss vs Number of Turns ({fiber_type_var.get()})")
            ax_entire3.grid(True)
            ax_entire3.legend()
        fig_entire.tight_layout()
        fig_entire.savefig(file_path)
        plt.close(fig_entire)
        result_label.config(text=f"Entire figure saved as: {file_path}")

# --- Responsive Font Size ---
def update_font_size(event):
    new_size = max(int(event.width / 50), 10)
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=new_size)
    plt.rcParams.update({'font.size': new_size})

# --- Create the main GUI window and layout ---
root = tk.Tk()
root.title("Optical Fiber Simulation App")
root.bind("<Configure>", update_font_size)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
root.rowconfigure(0, weight=1)

# Input frame on the left
input_frame = ttk.Frame(root, padding="10")
input_frame.grid(row=0, column=0, sticky="nsew")

# Fiber type selection
ttk.Label(input_frame, text="Select Fiber Type:").grid(row=0, column=0, sticky="W")
fiber_type_var = tk.StringVar(value="G.652D")
fiber_type_menu = ttk.Combobox(input_frame, textvariable=fiber_type_var,
                               values=list(fiber_types.keys()), state="readonly", width=10)
fiber_type_menu.grid(row=0, column=1, sticky="W")
fiber_type_var.trace("w", update_fiber_description)

# Display fiber description
fiber_desc_label = ttk.Label(input_frame, text="", wraplength=300)
fiber_desc_label.grid(row=1, column=0, columnspan=4, pady=(5, 10))
update_fiber_description()

# Fiber Length Simulation inputs
ttk.Label(input_frame, text="Fiber Length Range (km):").grid(row=2, column=0, sticky="W")
length_start_entry = ttk.Entry(input_frame, width=5)
length_start_entry.insert(0, "0.1")
length_start_entry.grid(row=2, column=1, sticky="W")
ttk.Label(input_frame, text="to").grid(row=2, column=2, sticky="W")
length_end_entry = ttk.Entry(input_frame, width=5)
length_end_entry.insert(0, "10")
length_end_entry.grid(row=2, column=3, sticky="W")

# Ambient temperature input
ttk.Label(input_frame, text="Ambient Temperature (°C):").grid(row=3, column=0, sticky="W")
temp_entry = ttk.Entry(input_frame, width=5)
temp_entry.insert(0, "30")
temp_entry.grid(row=3, column=1, sticky="W")

# Bending radius for length simulation
ttk.Label(input_frame, text="Bending Radius (cm) [Length Sim]:").grid(row=4, column=0, sticky="W")
bend_entry = ttk.Entry(input_frame, width=5)
bend_entry.insert(0, "3")
bend_entry.grid(row=4, column=1, sticky="W")

# Bending Simulation inputs
ttk.Label(input_frame, text="Fixed Length for Bending Sim (km):").grid(row=5, column=0, sticky="W")
fixed_length_bending_entry = ttk.Entry(input_frame, width=5)
fixed_length_bending_entry.insert(0, "5")
fixed_length_bending_entry.grid(row=5, column=1, sticky="W")
ttk.Label(input_frame, text="Bending Radius Range (cm): From").grid(row=5, column=2, sticky="W")
bend_from_entry = ttk.Entry(input_frame, width=5)
bend_from_entry.insert(0, "2")
bend_from_entry.grid(row=5, column=3, sticky="W")
ttk.Label(input_frame, text="To").grid(row=5, column=4, sticky="W")
bend_to_entry = ttk.Entry(input_frame, width=5)
bend_to_entry.insert(0, "10")
bend_to_entry.grid(row=5, column=5, sticky="W")

# Turns Simulation inputs
ttk.Label(input_frame, text="Fixed Length for Turns Sim (km):").grid(row=6, column=0, sticky="W")
fixed_length_turns_entry = ttk.Entry(input_frame, width=5)
fixed_length_turns_entry.insert(0, "5")
fixed_length_turns_entry.grid(row=6, column=1, sticky="W")
ttk.Label(input_frame, text="Bending Radius for Turns Sim (cm):").grid(row=6, column=2, sticky="W")
bend_turns_entry = ttk.Entry(input_frame, width=5)
bend_turns_entry.insert(0, "3")
bend_turns_entry.grid(row=6, column=3, sticky="W")
ttk.Label(input_frame, text="Turn Range: From").grid(row=6, column=4, sticky="W")
turn_from_entry = ttk.Entry(input_frame, width=5)
turn_from_entry.insert(0, "1")
turn_from_entry.grid(row=6, column=5, sticky="W")
ttk.Label(input_frame, text="To").grid(row=6, column=6, sticky="W")
turn_to_entry = ttk.Entry(input_frame, width=5)
turn_to_entry.insert(0, "20")
turn_to_entry.grid(row=6, column=7, sticky="W")

# Simulation buttons
simulate_length_button = ttk.Button(input_frame, text="Run Length Simulation", command=run_length_simulation)
simulate_length_button.grid(row=7, column=0, columnspan=2, pady=10)
simulate_bending_button = ttk.Button(input_frame, text="Run Bending Simulation", command=run_bending_simulation)
simulate_bending_button.grid(row=7, column=2, columnspan=2, pady=10)
simulate_turns_button = ttk.Button(input_frame, text="Run Turns Simulation", command=run_turns_simulation)
simulate_turns_button.grid(row=7, column=4, columnspan=2, pady=10)

# Save buttons for individual graphs and entire figure
save_length_button = ttk.Button(input_frame, text="Save Length Graph", command=save_length_graph)
save_length_button.grid(row=8, column=0, columnspan=2, pady=5)
save_bending_button = ttk.Button(input_frame, text="Save Bending Graph", command=save_bending_graph)
save_bending_button.grid(row=8, column=2, columnspan=2, pady=5)
save_turns_button = ttk.Button(input_frame, text="Save Turns Graph", command=save_turns_graph)
save_turns_button.grid(row=8, column=4, columnspan=2, pady=5)
save_entire_button = ttk.Button(input_frame, text="Save Entire Figure", command=save_entire_graph)
save_entire_button.grid(row=8, column=6, columnspan=2, pady=5)

# Result label
result_label = ttk.Label(root, text="Results will be shown here.", padding="10")
result_label.grid(row=9, column=0, sticky="W")

# Create Notebook for simulation graphs
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=1, rowspan=10, sticky="nsew", padx=10, pady=10)

# Tab for Length Simulation
tab_length = ttk.Frame(notebook)
notebook.add(tab_length, text="Length Simulation")
fig_length, ax_length = plt.subplots(figsize=(5,4))
canvas_length = FigureCanvasTkAgg(fig_length, master=tab_length)
canvas_length.get_tk_widget().pack(fill="both", expand=True)

# Tab for Bending Simulation
tab_bending = ttk.Frame(notebook)
notebook.add(tab_bending, text="Bending Simulation")
fig_bending, ax_bending = plt.subplots(figsize=(5,4))
canvas_bending = FigureCanvasTkAgg(fig_bending, master=tab_bending)
canvas_bending.get_tk_widget().pack(fill="both", expand=True)

# Tab for Turns Simulation
tab_turns = ttk.Frame(notebook)
notebook.add(tab_turns, text="Turns Simulation")
fig_turns, ax_turns = plt.subplots(figsize=(5,4))
canvas_turns = FigureCanvasTkAgg(fig_turns, master=tab_turns)
canvas_turns.get_tk_widget().pack(fill="both", expand=True)

# Configure grid responsiveness
for i in range(2):
    root.columnconfigure(i, weight=1)
for i in range(10):
    root.rowconfigure(i, weight=1)

root.mainloop()
