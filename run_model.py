import numpy as np

# --- 0. Define Constants ---
N = 500  # 500 sequences in each file
M = 4    # Our chosen filter length (M).

print(f"--- Generating input.txt (N={N}) ---")

# ---  Generate Test Data ---
time = np.linspace(0, 10, N)
# use different signals
desired_signal = np.sin(time) + 0.5 * np.sin(time * 0.5)
noise_white = 0.5 * np.random.randn(N)
input_signal_1 = desired_signal + noise_white

# --- Create the single input.txt file ---
# We will write 500 desired floats, THEN 500 input floats.
# Total = 1000 floats.
combined_input = np.concatenate((desired_signal, input_signal_1))

# Save as a text file, one number per line
# Using high precision to avoid rounding errors
np.savetxt("input.txt", combined_input, fmt="%.1f")

print(f"--- input.txt created with {len(combined_input)} floats. ---")