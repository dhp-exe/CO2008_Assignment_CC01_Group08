import numpy as np
import os
import glob

# Filter length M 
M = 10

def run_test_case(folder_path):
    # Print separator for clarity
    print(f"\n{'-'*20} {os.path.basename(folder_path)} {'-'*20}")

    # Construct paths
    desired_file = os.path.join(folder_path, "desired.txt")
    input_file = os.path.join(folder_path, "input.txt")
    expected_file = os.path.join(folder_path, "expected.txt")

    # Load Data
    try:
        desired_signal = np.loadtxt(desired_file)
        input_signal = np.loadtxt(input_file)
    except IOError as e:
        print(f"Error loading files: {e}")
        return

    N = desired_signal.shape[0]

    # --- ORIGINAL PRINT FORMAT ---
    print(f"\nDesired signal (N={N}): {desired_signal}")
    print(f"Input signal (N={N}):   {input_signal}")

    # Check for size mismatch
    if desired_signal.shape[0] != input_signal.shape[0]:
        print("\nError: size not match")
        return

    # --- CALCULATIONS ---
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
        return

    # apply the Filter to Get Output y(n) (output_signal)
    output_signal_full = np.convolve(input_signal, optimize_coefficient, mode='full')
    output_signal = output_signal_full[:N]

    # calculate MMSE
    error = desired_signal - output_signal
    mmse = np.mean(error ** 2)         
    print(f" MMSE = {mmse:.4f}")


    # --- RESULTS & CHECKING ---
    print("\n Results:")
    
    # --- Handle -0.0 rounding issue ---
    formatted_vals = []
    for val in output_signal:
        # Format to 1 decimal place first
        s = f"{val:.1f}"
        # Check if it resulted in negative zero and fix it
        if s == "-0.0":
            s = "0.0"
        formatted_vals.append(s)
    
    output_str = " ".join(formatted_vals)
    my_mmse_str = f"{mmse:.1f}"
    
    # 2. Print them (Original Format)
    print(f"Filtered output: {output_str}")
    print(f"MMSE: {my_mmse_str}")

    # 3. Verify against expected.txt
    if os.path.exists(expected_file):
        print("\n Verification:")
        try:
            with open(expected_file, 'r') as f:
                content = f.read()
                
            # Parse 'Filtered output' from file
            expected_output_line = [line for line in content.split('\n') if "Filtered output:" in line]
            expected_out_str = ""
            if expected_output_line:
                 # Split by ':' and strip whitespace
                expected_out_str = expected_output_line[0].split(":")[1].strip()

            # Parse 'MMSE' from file
            expected_mmse_line = [line for line in content.split('\n') if "MMSE:" in line]
            expected_mmse_val = ""
            if expected_mmse_line:
                expected_mmse_val = expected_mmse_line[0].split(":")[1].strip()

            # Perform the check
            output_match = (output_str == expected_out_str)
            mmse_match = (my_mmse_str == expected_mmse_val)

            if output_match and mmse_match:
                print(" [PASS] Output matches expected.txt exactly.")
            else:
                print(" [FAIL] Output mismatch.")
                if not output_match:
                    print(f"  Expected output: {expected_out_str}")
                    print(f"  Actual output:   {output_str}")
                if not mmse_match:
                    print(f"  Expected MMSE:   {expected_mmse_val}")
                    print(f"  Actual MMSE:     {my_mmse_str}")

        except Exception as e:
            print(f" [Warning] Could not parse expected.txt: {e}")
    else:
        print(" [Info] No expected.txt found for verification.")


def main():
    test_folders = sorted(glob.glob(os.path.join("tests", "test_*")))
    
    if not test_folders:
        print("No test folders found.")
        return

    for folder in test_folders:
        if os.path.isdir(folder):
            run_test_case(folder)

if __name__ == "__main__":
    main()