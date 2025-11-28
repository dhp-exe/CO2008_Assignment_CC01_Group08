import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_mmse_for_m(M, input_signal, desired_signal):
    N = input_signal.shape[0]
    
    # --- Logic from test.py ---
    # 1. Calculate Autocorrelation Matrix R_M
    rxx_full = np.correlate(input_signal, input_signal, mode='full')
    zero_lag_index = N - 1

    R_M = np.zeros((M, M))
    for l in range(M):
        for k in range(M):
            lag = l - k
            idx = zero_lag_index + lag
            if 0 <= idx < len(rxx_full):
                R_M[l, k] = rxx_full[idx]

    # 2. Calculate Cross-Correlation Vector gamma_d
    rdx_full = np.correlate(desired_signal, input_signal, mode='full')
    gamma_d = rdx_full[zero_lag_index : zero_lag_index + M]

    # 3. Solve for optimized Filter Coefficients h_opt
    try:
        optimize_coefficient = np.linalg.solve(R_M, gamma_d)
    except np.linalg.LinAlgError:
        return None  # Handle singular matrices for large M

    # 4. Apply the Filter
    output_signal_full = np.convolve(input_signal, optimize_coefficient, mode='full')
    output_signal = output_signal_full[:N]

    # 5. Calculate MMSE
    error = desired_signal - output_signal
    mmse = np.mean(error ** 2)
    return mmse

def main():
    # File paths (Test Mode 1)
    input_file = "input.txt"
    desired_file = "desired.txt"

    if os.path.exists(input_file) and os.path.exists(desired_file):
        print("Loading data...")
        input_data = np.loadtxt(input_file)
        desired_data = np.loadtxt(desired_file)
        
        # Define range of M to test (e.g., 1 to 15)
        # Ensure M doesn't exceed signal length
        max_M = min(15, len(input_data))
        M_values = range(1, max_M + 1)
        
        mmse_values = []
        valid_Ms = []

        print(f"Calculating MMSE for M = 1 to {max_M}...")
        for m in M_values:
            mmse = calculate_mmse_for_m(m, input_data, desired_data)
            if mmse is not None:
                mmse_values.append(mmse)
                valid_Ms.append(m)
                print(f" M={m}: MMSE={mmse:.4f}")
        
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(valid_Ms, mmse_values, marker='o', linestyle='-', color='b')
        plt.title('Relationship between Filter Length (M) and MMSE')
        plt.xlabel('Filter Length (M)')
        plt.ylabel('MMSE')
        plt.grid(True)
        plt.xticks(valid_Ms)
        
        output_plot = "mmse_vs_m_plot.png"
        plt.savefig(output_plot)
        print(f"\nPlot saved to {output_plot}")
        plt.show()
    else:
        print("Error: 'input.txt' and 'desired.txt' not found in the current directory.")

def plot_signal_comparison():
    # File names
    file_desired = "desired.txt"
    file_input2 = "input_2.txt"
    file_input3 = "input_3.txt"

    # Check if files exist
    if not (os.path.exists(file_desired) and os.path.exists(file_input2) and os.path.exists(file_input3)):
        print(f"Error: Make sure '{file_desired}', '{file_input2}', and '{file_input3}' are in the current folder.")
        return

    try:
        # Load data
        print("Loading data...")
        desired = np.loadtxt(file_desired)
        input2 = np.loadtxt(file_input2)
        input3 = np.loadtxt(file_input3)

        # Create Plot
        plt.figure(figsize=(12, 6))

        # Plot 1: Desired Signal (Reference)
        plt.plot(desired, label='Desired Signal (desired.txt)', color='black', linewidth=2, linestyle='--')

        # Plot 2: Input 2
        plt.plot(input2, label='Input 2 (input_2.txt)', color='blue', alpha=0.7)

        # Plot 3: Input 3
        plt.plot(input3, label='Input 3 (input_3.txt)', color='red', alpha=0.7)

        # Formatting
        plt.title('Desired vs Input 2 vs Input 3')
        plt.xlabel('Sample Index (n)')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)

        # Save and Show
        output_filename = 'signal_comparison.png'
        plt.savefig(output_filename)
        print(f"Plot saved successfully to '{output_filename}'")
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    #main()
    plot_signal_comparison()