import numpy as np
import matplotlib.pyplot as plt

# --- Part 1: Numerical Aperture Calculation ---
def calculate_numerical_aperture(D, b):
    """
    Calculate the acceptance angle and numerical aperture.
    D: diameter of the spot (mm)
    b: distance from fiber end to screen (mm)
    """
    # Convert degrees to radians in calculation
    theta = np.arctan(D / (2 * b))  # in radians
    NA = np.sin(theta)
    # Convert theta to degrees for display
    theta_deg = np.degrees(theta)
    return theta_deg, NA

# Example values: D = 1.15 mm, b = 100 mm (you can adjust b based on your setup)
D = 1.15
b = 100.0
theta_deg, NA = calculate_numerical_aperture(D, b)
print(f"Calculated acceptance angle: {theta_deg:.2f} degrees")
print(f"Calculated Numerical Aperture (NA): {NA:.4f}")

# --- Part 2: Attenuation and Bending Loss Simulation ---

# Define simulation parameters:
attenuation_coeff = 0.00385  # Attenuation per km (in dB/km)
base_bending_loss = 0.1      # Assume base loss of 0.1 dB for a 90° bend with ideal bending radius

def bending_loss_per_bend(bend_radius, bend_angle_deg):
    """
    Model bending loss per bend:
    - Loss increases as bending radius decreases.
    - For a 90° bend, base loss is given (e.g., 0.1 dB for an ideal radius).
    - For other bend angles, scale linearly.
    """
    # For simplicity, assume loss scales inversely with bending radius (in cm) and linearly with bend angle.
    # Normalize with an ideal radius, say R_ideal = 10 cm (example value)
    R_ideal = 10.0  # cm
    angle_factor = bend_angle_deg / 90.0  # 90° as base
    loss = base_bending_loss * (R_ideal / bend_radius) * angle_factor
    return loss

# Simulation for fiber length (km)
fiber_lengths = np.linspace(0, 10, 100)  # 0 to 10 km
# Assume a fixed number of bends (e.g., 5 bends along the fiber)
number_of_bends = 5
# Assume constant bending conditions:
bend_radius = 5.0   # cm (adjustable)
bend_angle = 90.0   # degrees

# Calculate total loss for each fiber length:
total_loss = []
loss_per_bend = bending_loss_per_bend(bend_radius, bend_angle)
for L in fiber_lengths:
    # Attenuation loss (dB) over fiber length:
    loss_attenuation = attenuation_coeff * L
    # Total bending loss is independent of fiber length if number of bends is fixed:
    loss_bending = number_of_bends * loss_per_bend
    total_loss.append(loss_attenuation + loss_bending)

# Plotting the losses vs fiber length:
plt.figure(figsize=(8, 5))
plt.plot(fiber_lengths, total_loss, label="Total Loss (Attenuation + Bending)")
plt.plot(fiber_lengths, [attenuation_coeff * L for L in fiber_lengths], '--', label="Attenuation Loss Only")
plt.xlabel("Fiber Length (km)")
plt.ylabel("Loss (dB)")
plt.title("Simulated Optical Fiber Loss")
plt.legend()
plt.grid(True)
plt.show()

# Additional plot: Bending loss vs bending radius for a fixed bend angle
bend_radii = np.linspace(2, 20, 100)  # from 2 cm to 20 cm
bending_losses = [bending_loss_per_bend(R, bend_angle) for R in bend_radii]

plt.figure(figsize=(8, 5))
plt.plot(bend_radii, bending_losses)
plt.xlabel("Bending Radius (cm)")
plt.ylabel("Loss per Bend (dB)")
plt.title("Bending Loss vs Bending Radius")
plt.grid(True)
plt.show()
