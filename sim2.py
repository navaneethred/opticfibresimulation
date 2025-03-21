import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Part 1: Numerical Aperture Calculation
# -------------------------------
def calculate_numerical_aperture(D, b):
    """
    Calculate the acceptance angle and numerical aperture.
    
    Parameters:
      D: Diameter of the laser spot (mm)
      b: Distance from fiber end to screen (mm)
      
    Returns:
      theta_deg: Acceptance angle in degrees
      NA: Numerical Aperture
    """
    theta = np.arctan(D / (2 * b))  # in radians
    NA = np.sin(theta)
    theta_deg = np.degrees(theta)
    return theta_deg, NA

# Example experimental values:
D = 1.15   # mm (spot diameter)
b = 100.0  # mm (distance to screen)

theta_deg, NA = calculate_numerical_aperture(D, b)
print(f"Calculated acceptance angle: {theta_deg:.2f}°")
print(f"Calculated Numerical Aperture (NA): {NA:.4f}")

# -------------------------------
# Part 2: Enhanced Fiber Loss Simulation
# -------------------------------

# Parameters based on your experiment and typical real-life values:
I_in = 1000.0  # Input current in µA
attenuation_coeff = 0.00385  # Attenuation loss in dB/km (measured)
base_bending_loss = 0.2      # Base bending loss in dB for a 90° bend at ideal radius (example)
number_of_bends = 5          # Total number of bends in the fiber
bend_angle = 90.0            # Bend angle in degrees (per bend)
ideal_bend_radius = 10.0     # Ideal bending radius in cm for minimum loss

def bending_loss(bend_radius, bend_angle_deg):
    """
    Calculate the loss per bend.
    
    The loss is modeled as inversely proportional to the bending radius and
    directly proportional to the bend angle (normalized to 90°).
    
    Parameters:
      bend_radius: Actual bending radius (cm)
      bend_angle_deg: Bend angle in degrees
      
    Returns:
      Loss per bend in dB.
    """
    loss = base_bending_loss * (ideal_bend_radius / bend_radius) * (bend_angle_deg / 90.0)
    return loss

# Temperature effect parameters:
room_temperature = 25.0      # °C
temp_coefficient = 0.0002    # Additional attenuation in dB/km per °C deviation

def simulate_output_current(fiber_length, bend_radius, ambient_temp, noise_std=0.02):
    """
    Simulate the output current (in µA) for a given fiber length with specified bending and temperature conditions.
    
    Parameters:
      fiber_length: Length of the fiber in km
      bend_radius: Bending radius in cm
      ambient_temp: Operating temperature in °C
      noise_std: Standard deviation for measurement noise (fractional noise)
      
    Returns:
      I_out: Output current in µA
      total_loss: Total loss in dB
    """
    # Attenuation loss over the fiber (dB)
    loss_attenuation = attenuation_coeff * fiber_length
    
    # Additional loss due to temperature deviation from room temperature:
    temp_loss = temp_coefficient * abs(ambient_temp - room_temperature) * fiber_length
    
    # Bending loss: loss per bend multiplied by number of bends.
    loss_per_bend = bending_loss(bend_radius, bend_angle)
    total_bending_loss = number_of_bends * loss_per_bend
    
    # Total loss in dB:
    total_loss = loss_attenuation + total_bending_loss + temp_loss
    
    # Convert dB loss to linear scale current measurement:
    I_out = I_in * 10 ** (-total_loss / 10)
    
    # Introduce random measurement noise (Gaussian noise, scaled to the current)
    noise = np.random.normal(0, noise_std * I_out)
    I_out_noisy = I_out + noise
    
    return I_out_noisy, total_loss

# Simulation over a range of fiber lengths
fiber_lengths = np.linspace(0.1, 10, 100)  # in km, avoiding 0 km to prevent trivial division issues
ambient_temp = 30.0    # Example: operating temperature in °C
bend_radius = 5.0      # cm (a tighter bend than ideal)

output_currents = []
losses = []

for L in fiber_lengths:
    I_out, tot_loss = simulate_output_current(L, bend_radius, ambient_temp)
    output_currents.append(I_out)
    losses.append(tot_loss)

# Plot Output Current vs Fiber Length
plt.figure(figsize=(8, 5))
plt.plot(fiber_lengths, output_currents, label="Simulated Output Current (µA)")
plt.xlabel("Fiber Length (km)")
plt.ylabel("Output Current (µA)")
plt.title("Simulated Output Current vs. Fiber Length")
plt.legend()
plt.grid(True)
plt.show()

# -------------------------------
# Additional Simulation: Varying Temperature Effects
# -------------------------------
temperatures = np.linspace(20, 40, 100)  # °C range from 20°C to 40°C
fixed_length = 5.0  # km

currents_temp = []
for T in temperatures:
    I_out, _ = simulate_output_current(fixed_length, bend_radius, T)
    currents_temp.append(I_out)

plt.figure(figsize=(8, 5))
plt.plot(temperatures, currents_temp, color='orange', label="Output Current (µA)")
plt.xlabel("Ambient Temperature (°C)")
plt.ylabel("Output Current (µA)")
plt.title("Effect of Temperature on Output Current (Fixed Fiber Length)")
plt.legend()
plt.grid(True)
plt.show()

# -------------------------------
# Additional Simulation: Impact of Bending Radius Variation
# -------------------------------
bend_radii = np.linspace(2, 20, 100)  # from 2 cm to 20 cm
currents_bend = []
for R in bend_radii:
    I_out, _ = simulate_output_current(fixed_length, R, ambient_temp)
    currents_bend.append(I_out)

plt.figure(figsize=(8, 5))
plt.plot(bend_radii, currents_bend, color='green', label="Output Current (µA)")
plt.xlabel("Bending Radius (cm)")
plt.ylabel("Output Current (µA)")
plt.title("Impact of Bending Radius on Output Current (Fixed Fiber Length)")
plt.legend()
plt.grid(True)
plt.show()
