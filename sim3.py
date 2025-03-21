import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
I_in = 1000.0  # Input current in µA
num_rays = 100000  # Number of rays to simulate
fiber_length = 5.0  # Fiber length in km
attenuation_coeff = 0.00385  # Attenuation in dB/km
room_temp = 25.0  # Reference temperature in °C
ambient_temp = 30.0  # Operating temperature in °C
temp_coefficient = 0.0002  # dB/km/°C
number_of_bends = 5  # Fixed number of bends along the fiber
ideal_bend_radius = 10.0  # cm
base_bending_loss = 0.2  # dB loss for a 90° bend at ideal radius

# Define a function to compute bending loss per bend based on a randomly perturbed bending radius
def random_bending_loss():
    # Introduce a small random variation around a given bending radius (in cm)
    bend_radius = np.random.normal(loc=5.0, scale=0.5)  # e.g., mean 5 cm, small std dev
    # Ensure bend_radius remains positive
    bend_radius = max(bend_radius, 1.0)
    loss = base_bending_loss * (ideal_bend_radius / bend_radius)
    return loss

# Monte Carlo simulation for ray propagation
def simulate_ray():
    # Compute attenuation loss over the fiber (dB)
    loss_attenuation = attenuation_coeff * fiber_length
    # Temperature effect (dB)
    loss_temp = temp_coefficient * abs(ambient_temp - room_temp) * fiber_length
    # Sum bending losses for this ray, each bend can have random variations
    total_bending_loss = sum(random_bending_loss() for _ in range(number_of_bends))
    # Total loss for the ray
    total_loss = loss_attenuation + total_bending_loss + loss_temp
    # Convert total loss in dB to a power ratio and then to output current
    I_out = I_in * 10 ** (-total_loss / 10)
    return I_out, total_loss

# Simulate many rays and average the output current
ray_outputs = []
ray_losses = []
for _ in range(num_rays):
    I_out, loss = simulate_ray()
    ray_outputs.append(I_out)
    ray_losses.append(loss)

avg_I_out = np.mean(ray_outputs)
std_I_out = np.std(ray_outputs)

print(f"Average Output Current: {avg_I_out:.2f} µA")
print(f"Standard Deviation: {std_I_out:.2f} µA")

# Plot a histogram of the simulated output currents
plt.figure(figsize=(8, 5))
plt.hist(ray_outputs, bins=30, color='skyblue', edgecolor='black')
plt.xlabel("Output Current (µA)")
plt.ylabel("Number of Rays")
plt.title("Distribution of Output Current from Monte Carlo Ray-Tracing Simulation")
plt.grid(True)
plt.show()
