import numpy as np

# --- 0. Define Constants ---
N = 500  # 500 sequences in each file
M = 4    # Our chosen filter length (M).

print(f"--- Generating input.txt (N={N}) ---")

# ---  Generate Test Data ---
#
# *** FIX: Use random "white noise" as the base signal, not a sine wave. ***
#     A rounded sine wave creates repeating numbers (e.g., 0.1, 0.1, 0.1),
#     which results in a singular (unsolvable) matrix.
#     A rounded *random* signal will not have this problem.
#
desired_signal = np.random.randn(N)
noise_white = 0.5 * np.random.randn(N) # Per assignment, add noise
input_signal_1 = desired_signal + noise_white

# --- Create the single input.txt file ---
# We will write 500 desired floats, THEN 500 input floats.
# Total = 1000 floats.
combined_input = np.concatenate((desired_signal, input_signal_1))

#
# *** Save using "%.1f" as required by the assignment spec. ***
#
np.savetxt("input.txt", combined_input, fmt="%.1f")

print(f"--- input.txt (%.1f) created with {len(combined_input)} floats. ---")