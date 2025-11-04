import numpy as np

# Constants
N = 10   # 10 samples 
M = 4    # Filter length

print(f"--- Starting Wiener Filter Model (N={N}, M={M}) ---")

# --- Generate Desired and Noisy Input ---
print("Generating input.txt with 20 numbers (10 desired + 10 input)...")

# Desired signal: a simple sine wave
time = np.linspace(0, 2 * np.pi, N)
desired_signal = np.sin(time)

# Generate white noise
noise = 0.2 * np.random.randn(N)

# Input signal with noise: d(n) = s(n) + w(n)
input_signal = desired_signal + noise

# Create input.txt with 20 numbers (first 10 desired, last 10 input)
combined_signal = np.concatenate([desired_signal, input_signal])
np.savetxt("input.txt", combined_signal, fmt="%.1f")

# Also save individual files for reference
np.savetxt("desired.txt", desired_signal, fmt="%.1f")
np.savetxt("input_signal.txt", input_signal, fmt="%.1f")


# --- Load Data from input.txt ---
print("\nLoading data from input.txt...")
combined_data = np.loadtxt("input.txt")

# Split into desired and input signals
desired_signal = combined_data[:N]  # First 10 numbers
input_signal = combined_data[N:]    # Last 10 numbers

print(f"\nDesired signal: {desired_signal}")
print(f"\nInput signal: {input_signal}")

# Check for size mismatch
if desired_signal.shape[0] != input_signal.shape[0]:
    print("Error: size not match")
    exit()

# --- Calculate Autocorrelation Matrix R_M ---
print("\nCalculating Autocorrelation Matrix (R_M)...")
rxx_full = np.correlate(input_signal, input_signal, mode='full')
zero_lag_index = N - 1

R_M = np.zeros((M, M))
for l in range(M):
    for k in range(M):
        lag = l - k
        R_M[l, k] = rxx_full[zero_lag_index + lag]

# --- Calculate Cross-Correlation Vector gamma_d ---
print("\nCalculating Cross-Correlation Vector (gamma_d)...")
rdx_full = np.correlate(desired_signal, input_signal, mode='full')
gamma_d = rdx_full[zero_lag_index : zero_lag_index + M]

# --- Solve for Filter Coefficients (optimize_coefficient) ---
print("\nSolving for optimize_coefficient...")
optimize_coefficient = np.linalg.solve(R_M, gamma_d)
print(f"- Coefficients: {optimize_coefficient}")

# --- Apply the Filter to Get Output (output_signal) ---
print("\nApplying Wiener filter...")
output_signal_full = np.convolve(input_signal, optimize_coefficient, mode='full')
output_signal = output_signal_full[:N]

# --- Calculate MMSE ---
print("Calculating MMSE...")
error = desired_signal - output_signal
mmse = np.mean(error ** 2)         
print(f"   ... MMSE = {mmse:.4f}")

# --- Print Results to Terminal ---
print("\n--- Final Results ---")
output_str = " ".join([f"{val:.1f}" for val in output_signal])
print("Filtered output:")
print(output_str)
print(f"MMSE: {mmse:.4f}")

# # --- Write Results to output.txt ---
# print("\nWriting output.txt...")
# with open("output.txt", "w") as f:
#     f.write("Filtered output:\n")
#     f.write(output_str + "\n")
#     f.write(f"MMSE: {mmse:.2f}\n")


