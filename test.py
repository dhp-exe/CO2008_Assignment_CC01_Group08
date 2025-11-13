import numpy as np

# Filter length M 
M = 4

try:
    desired_signal = np.loadtxt("desired.txt")
    input_signal = np.loadtxt("input.txt")
except IOError as e:
    print(f"Error loading files: {e}")
    exit()

N = desired_signal.shape[0]

print(f"\nDesired signal (N={N}): {desired_signal}")
print(f"Input signal (N={N}):   {input_signal}")

# Check for size mismatch
if desired_signal.shape[0] != input_signal.shape[0]:
    print("\nError: size not match")
    exit()

# calculate Autocorrelation Matrix R_M
rxx_full = np.correlate(input_signal, input_signal, mode='full')
zero_lag_index = N - 1

R_M = np.zeros((M, M))
for l in range(M):
    for k in range(M):
        lag = l - k
        R_M[l, k] = rxx_full[zero_lag_index + lag]

# calculate Cross-Correlation Vector gamma_d
rdx_full = np.correlate(desired_signal, input_signal, mode='full')
gamma_d = rdx_full[zero_lag_index : zero_lag_index + M]

# solve for optimized Filter Coefficients h_opt
try:
    optimize_coefficient = np.linalg.solve(R_M, gamma_d)
    print(f"h_opt: {optimize_coefficient}")
except np.linalg.LinAlgError:
    print("Error: cannot solve for coefficients.")
    exit()

# apply the Filter to Get Output y(n) (output_signal)
output_signal_full = np.convolve(input_signal, optimize_coefficient, mode='full')
output_signal = output_signal_full[:N]

# calculate MMSE
error = desired_signal - output_signal
mmse = np.mean(error ** 2)         
print(f" MMSE = {mmse:.4f}")


print("\n Results:")
output_str = " ".join([f"{val:.1f}" for val in output_signal])
print(f"Filtered output: {output_str}")
print(f"MMSE: {mmse:.1f}")
