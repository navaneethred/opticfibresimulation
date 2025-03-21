import numpy as np
import matplotlib.pyplot as plt

def hybrid_simulation(I_in, fiber_length_km, num_steps, num_bend_events, ambient_temp, room_temp, 
                      attenuation_coeff, temp_coefficient, noise_std):
    """
    Hybrid simulation that combines deterministic BPM-like propagation with random bending loss events.
    
    Parameters:
      I_in              : Input current in µA
      fiber_length_km   : Total fiber length (km)
      num_steps         : Number of steps to discretize the fiber
      num_bend_events   : Number of random bending loss events along the fiber
      ambient_temp      : Operating ambient temperature (°C)
      room_temp         : Reference room temperature (°C)
      attenuation_coeff : Attenuation coefficient (dB/km)
      temp_coefficient  : Additional loss coefficient (dB/km/°C)
      noise_std         : Standard deviation for fractional noise
      
    Returns:
      I_out_noisy       : Final output current in µA (with noise)
      loss_profile      : List of cumulative loss in dB along the fiber
      bend_event_indices: Indices of steps where bending events occurred
    """
    dz = fiber_length_km / num_steps  # km per step
    total_loss_dB = 0.0
    loss_profile = []
    
    # Randomly select indices for bending events (Monte Carlo component)
    bend_event_indices = np.sort(np.random.choice(np.arange(num_steps), num_bend_events, replace=False))
    
    for step in range(num_steps):
        # Deterministic losses:
        # Attenuation loss over the step:
        loss_attenuation = attenuation_coeff * dz
        # Temperature loss if operating away from room temperature:
        loss_temp = temp_coefficient * abs(ambient_temp - room_temp) * dz
        total_loss_dB += loss_attenuation + loss_temp
        
        # In a full BPM simulation, here you would propagate the optical field.
        # For this example, we assume no diffraction or modal changes affecting amplitude.
        
        # Monte Carlo event: apply additional bending loss if this step is selected
        if step in bend_event_indices:
            # Random bending loss per event (mean 0.2 dB, small variability)
            bending_loss_dB = np.random.normal(loc=0.2, scale=0.05)
            total_loss_dB += bending_loss_dB
        
        loss_profile.append(total_loss_dB)
        
    # Convert cumulative loss (in dB) to output current:
    I_out = I_in * 10 ** (-total_loss_dB / 10)
    
    # Add measurement noise:
    noise = np.random.normal(0, noise_std * I_out)
    I_out_noisy = I_out + noise
    
    return I_out_noisy, loss_profile, bend_event_indices

# Parameters (adjust as needed for your experiment)
I_in = 1000.0           # Input current in µA
fiber_length = 5.0      # Total fiber length in km
num_steps = 500         # Discretization steps along fiber length
num_bend_events = 10    # Number of random bending events
ambient_temp = 30.0     # Operating temperature (°C)
room_temp = 25.0        # Reference room temperature (°C)
attenuation_coeff = 0.00385  # Attenuation coefficient (dB/km)
temp_coefficient = 0.0002    # Temperature loss coefficient (dB/km/°C)
noise_std = 0.02             # 2% noise standard deviation

# Run the hybrid simulation
I_out_noisy, loss_profile, bend_events = hybrid_simulation(I_in, fiber_length, num_steps, 
                                                           num_bend_events, ambient_temp, room_temp, 
                                                           attenuation_coeff, temp_coefficient, noise_std)

print(f"Hybrid Simulation Output Current: {I_out_noisy:.2f} µA")

# Plot the cumulative loss along the fiber and mark bending events
z = np.linspace(0, fiber_length, num_steps)  # position in km
plt.figure(figsize=(8, 5))
plt.plot(z, loss_profile, label="Cumulative Loss (dB)")
plt.scatter(z[bend_events], np.array(loss_profile)[bend_events], color='red', label="Bending Events")
plt.xlabel("Fiber Length (km)")
plt.ylabel("Cumulative Loss (dB)")
plt.title("Hybrid Simulation: Loss Profile Along Fiber")
plt.legend()
plt.grid(True)
plt.show()
