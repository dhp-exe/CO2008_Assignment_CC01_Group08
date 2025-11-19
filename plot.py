import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import glob

def parse_expected_file(filepath):
    """
    Parses expected.txt to extract the signal and MMSE.
    """
    output_signal = []
    mmse = None
    
    if not os.path.exists(filepath):
        return np.array([]), None

    try:
        with open(filepath, 'r') as f:
            content = f.readlines()
            
        for line in content:
            if "Filtered output:" in line:
                numbers_str = line.split("Filtered output:")[1].strip()
                output_signal = [float(x) for x in numbers_str.split()]
            
            if "MMSE:" in line:
                mmse_str = line.split("MMSE:")[1].strip()
                mmse = float(mmse_str)
                
        return np.array(output_signal), mmse
    except Exception as e:
        print(f"[Error] Failed to parse {filepath}: {e}")
        return np.array([]), None

def load_data(folder_path):
    """Loads input.txt, desired.txt, and expected.txt from the folder."""
    data = {}
    try:
        data['input'] = np.loadtxt(os.path.join(folder_path, "input.txt"))
    except:
        data['input'] = np.array([])

    try:
        data['desired'] = np.loadtxt(os.path.join(folder_path, "desired.txt"))
    except:
        data['desired'] = np.array([])

    data['output'], data['mmse'] = parse_expected_file(os.path.join(folder_path, "expected.txt"))
    return data

def plot_signals(data, folder_name, save_path=None):
    """Generates the 6-subplot analysis grid."""
    desired = data.get('desired')
    input_signal = data.get('input')
    output = data.get('output')
    mmse = data.get('mmse')

    if len(desired) == 0 or len(input_signal) == 0:
        print("[Error] Missing input or desired signal data. Cannot plot.")
        return

    # Setup Figure: 3 Rows, 2 Columns
    fig = plt.figure(figsize=(14, 12))
    plt.suptitle(f'Wiener Filter Analysis - {folder_name}', fontsize=16, fontweight='bold')

    # 1. Combined: Desired vs Input (Noisy)
    ax1 = plt.subplot(3, 2, 1)
    plt.plot(desired, 'b-o', linewidth=1.5, label='Desired (Target)', alpha=0.8)
    plt.plot(input_signal, 'r--x', linewidth=1, alpha=0.5, label='Input (Noisy)')
    plt.title('1. Input vs Desired Signal', fontweight='bold')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')

    # 2. Output Signal
    ax2 = plt.subplot(3, 2, 2)
    if len(output) > 0:
        plt.plot(output, 'g-s', linewidth=1.5, label='Output (Filtered)')
        plt.title('2. Output Signal', fontweight='bold')
    else:
        plt.text(0.5, 0.5, 'No Output Data', ha='center')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')

    # 3. Comparison: Desired vs Output
    ax3 = plt.subplot(3, 2, 3)
    if len(output) > 0:
        min_len = min(len(desired), len(output))
        plt.plot(input_signal[:min_len], 'r--', linewidth=1.5, label='Input', alpha=0.3)
        plt.plot(desired[:min_len], 'b-', linewidth=1.5, label='Desired', alpha=0.5)
        plt.plot(output[:min_len], 'g--', linewidth=1.5, label='Output', alpha=0.9)
    plt.title('3. Comparison: Input vs Desired vs Output', fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')

    # 4. Error Signal
    ax4 = plt.subplot(3, 2, 4)
    error_signal = []
    if len(output) > 0:
        min_len = min(len(desired), len(output))
        error_signal = desired[:min_len] - output[:min_len]
        plt.plot(error_signal, 'purple', linewidth=1)
        mmse_text = f"(MMSE: {mmse:.4f})" if mmse is not None else ""
        plt.title(f'4. Error Signal {mmse_text}', fontweight='bold')
        plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    plt.grid(True, alpha=0.3)

    # 5. Error Histogram
    ax5 = plt.subplot(3, 2, 5)
    if len(error_signal) > 0:
        plt.hist(error_signal, bins=20, color='purple', alpha=0.7, edgecolor='black')
        plt.title('5. Error Distribution', fontweight='bold')
        plt.xlabel('Error Magnitude')
        plt.ylabel('Count')
    plt.grid(True, alpha=0.3)

    # 6. Frequency Spectrum (FFT)
    ax6 = plt.subplot(3, 2, 6)
    
    def plot_fft(sig, color, label, style='-'):
        if len(sig) == 0: return
        # Plot positive frequencies only
        freq = np.fft.fftfreq(len(sig))
        mag = np.abs(np.fft.fft(sig))
        mask = freq >= 0
        plt.plot(freq[mask], mag[mask], color=color, linestyle=style, alpha=0.7, label=label)

    plot_fft(input_signal, 'r', 'Input')
    plot_fft(desired, 'b', 'Desired')
    if len(output) > 0:
        plot_fft(output, 'g', 'Output', '--')
    
    plt.title('6. Frequency Spectrum', fontweight='bold')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Graph saved to: {save_path}")

def main():
    parser = argparse.ArgumentParser(description="Plot signals for a specific test case.")
    parser.add_argument("folder", nargs='?', help="Path to test folder (e.g. tests/test_001)")
    args = parser.parse_args()

    target_folder = args.folder

    # Default to first test if no folder specified
    if not target_folder:
        all_tests = sorted(glob.glob(os.path.join("tests", "test_*")))
        if all_tests:
            target_folder = all_tests[0]
            print(f"No folder specified. Defaulting to: {target_folder}")
        else:
            print("No test folders found!")
            return

    if os.path.isdir(target_folder):
        print(f"Plotting data from: {target_folder}")
        data = load_data(target_folder)
        save_loc = os.path.join(target_folder, "result_plot.png")
        plot_signals(data, os.path.basename(target_folder), save_path=save_loc)
    else:
        print(f"Error: Folder '{target_folder}' does not exist.")

if __name__ == "__main__":
    main()