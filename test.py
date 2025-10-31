import numpy as np

# --- 0. Define Constants ---
N = 500  # 500 sequences in each file
M = 4    # Our chosen filter length (M). Start small!

print(f"--- Starting Wiener Filter Model (N={N}, M={M}) ---")

# --- 1. Generate Test Data ---
print("Step 1: Generating test data...")
# Create a "desired" signal (e.g., a sine wave)
time = np.linspace(0, 10, N)
desired_signal = np.sin(time)

# Create "noise" signal (e.g., white noise)
# We'll create two noise types as required
noise_white = 0.5 * np.random.randn(N)
noise_colored = 0.2 * np.sin(time * 10) # Another noise type

# --- 2. Create Files ---
print("Step 2: Saving test files...")
# Create the first test case (desired + white noise)
input_signal_1 = desired_signal + noise_white

# Save the files. The MIPS program will read these.
# All numbers are floats rounded to 1 decimal point
np.savetxt("desired.txt", desired_signal, fmt="%.1f")
np.savetxt("noise_white.txt", noise_white, fmt="%.1f")
np.savetxt("input_1.txt", input_signal_1, fmt="%.1f")

# Create the second test case (desired + colored noise)
input_signal_2 = desired_signal + noise_colored
np.savetxt("noise_colored.txt", noise_colored, fmt="%.1f")
np.savetxt("input_2.txt", input_signal_2, fmt="%.1f")

print("   ... desired.txt, input_1.txt, input_2.txt created.")

# --- 3. Load Data ---
print("Step 3: Loading data for processing (using input_1.txt)...")
d = np.loadtxt("desired.txt")
x = np.loadtxt("input_1.txt") # Using test case 1

# Check for size mismatch
if d.shape[0] != x.shape[0]:
    print("Error: size not match")
    exit()

# --- 4. Calculate Autocorrelation Matrix R_M ---
print("Step 4: Calculating Autocorrelation Matrix (R_M)...")
# We need the autocorrelation of x, gamma_xx(k)
# 'full' computes the correlation for all lags
rxx_full = np.correlate(x, x, mode='full')

# The zero-lag (k=0) is at the center
zero_lag_index = N - 1

# Build the M x M Toeplitz matrix R_M
R_M = np.zeros((M, M))
for l in range(M):
    for k in range(M):
        lag = l - k
        # gamma_xx(lag) is at rxx_full[zero_lag_index + lag]
        R_M[l, k] = rxx_full[zero_lag_index + lag]
# print("R_M:\n", R_M) # Uncomment to debug

# --- 5. Calculate Cross-Correlation Vector gamma_d ---
print("Step 5: Calculating Cross-Correlation Vector (gamma_d)...")
# We need gamma_dx(l) for l = 0, 1, ..., M-1
rdx_full = np.correlate(d, x, mode='full')

# Get the lags from 0 to M-1
# gamma_dx(l) is at rdx_full[zero_lag_index + l]
gamma_d = rdx_full[zero_lag_index : zero_lag_index + M]
# print("gamma_d:\n", gamma_d) # Uncomment to debug

# --- 6. Solve for Filter Coefficients (h_opt) ---
print("Step 6: Solving for h_opt (optimize_coefficient)...")
# Solves the linear system R_M * h = gamma_d
h_opt = np.linalg.solve(R_M, gamma_d)
print(f"   ... h_opt calculated: {h_opt}")

# --- 7. Apply the Filter to Get Output (y_out) ---
print("Step 7: Applying filter to get output signal...")
# 'same' mode gives an output of the same length as the input (N)
y_out = np.convolve(x, h_opt, mode='same')

# --- 8. Calculate the MMSE ---
print("Step 8: Calculating final MMSE...")
# Calculate the error signal
e = d - y_out

# Calculate the mean-square error
mmse = np.mean(e**2)
print(f"   ... Final MMSE: {mmse}")

# --- 9. Write the Final Output File ---
print("Step 9: Writing final output.txt...")
with open("output.txt", "w") as f:
    # First, write all 500 output sequences
    for val in y_out:
        f.write(f"{val:.1f}\n") # Write as float with 1 decimal
    
    # Then, add the MM