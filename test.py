import numpy as np

# Filter length M 
M = 4    

print(f"--- Starting Wiener Filter Model (M={M}) ---")

print("\nLoading data from desired.txt and input.txt...")
try:
    desired_signal = np.loadtxt("desired.txt")
    input_signal = np.loadtxt("input.txt")
except IOError as e:
    print(f"Error loading files: {e}")
    print("Please make sure 'desired.txt' and 'input.txt' are in the same directory.")
    exit()

# N is determined from the loaded data
N = desired_signal.shape[0]

print(f"\nDesired signal (N={N}): {desired_signal}")
print(f"Input signal (N={N}):   {input_signal}")

# Check for size mismatch
if desired_signal.shape[0] != input_signal.shape[0]:
    print("\nError: size not match")
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
try:
    optimize_coefficient = np.linalg.solve(R_M, gamma_d)
    print(f"- Coefficients: {optimize_coefficient}")
except np.linalg.LinAlgError:
    print("Error: Autocorrelation matrix R_M is singular, cannot solve for coefficients.")
    exit()

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
print(f"Filtered output: {output_str}")
print(f"MMSE: {mmse:.1f}")
