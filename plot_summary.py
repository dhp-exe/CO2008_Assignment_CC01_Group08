import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# --- CONFIGURATION ---
TESTS_DIR = "tests"
OUTPUT_FILENAME = "combined_results.png"

def parse_expected_file(filepath):
    """
    Parses expected.txt to extract the output signal.
    """
    output_signal = []
    mmse = 0.0
    
    if not os.path.exists(filepath):
        return np.array([]), None

    try:
        with open(filepath, 'r') as f:
            content = f.readlines()
            
        for line in content:
            if "Filtered output:" in line:
                parts = line.split("Filtered output:")[1].strip().split()
                output_signal = [float(x) for x in parts]
            if "MMSE:" in line:
                 mmse = float(line.split("MMSE:")[1].strip())
                
        return np.array(output_signal), mmse
    except Exception as e:
        print(f"[Error] Failed to parse {filepath}: {e}")
        return np.array([]), None

def collect_data():
    """
    Iterates through all test folders and gathers error data.
    """
    test_folders = sorted(glob.glob(os.path.join(TESTS_DIR, "test_*")))
    results = []

    print(f"Found {len(test_folders)} test folders. Processing...")

    for folder in test_folders:
        test_name = os.path.basename(folder)
        
        desired_path = os.path.join(folder, "desired.txt")
        expected_path = os.path.join(folder, "expected.txt")

        # We need both files to calculate specific errors
        if os.path.exists(desired_path) and os.path.exists(expected_path):
            try:
                desired = np.loadtxt(desired_path)
                output, file_mmse = parse_expected_file(expected_path)

                if len(output) > 0:
                    # Match lengths just in case
                    min_len = min(len(desired), len(output))
                    desired = desired[:min_len]
                    output = output[:min_len]

                    # Calculate Error Signal
                    error_signal = desired - output
                    calculated_mmse = np.mean(error_signal ** 2)

                    results.append({
                        'name': test_name,
                        'mmse': calculated_mmse,
                        'error_signal': error_signal
                    })
            except Exception as e:
                print(f"Skipping {test_name}: {e}")
        else:
            print(f"Skipping {test_name}: Missing desired.txt or expected.txt")

    return results

def plot_combined_results(results):
    if not results:
        print("No valid results found to plot.")
        return

    # Extract data for plotting
    names = [r['name'].replace('test_', '') for r in results] # Shorten names
    mmses = [r['mmse'] for r in results]
    errors = [r['error_signal'] for r in results]

    # Create Figure (2 Subplots)
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    plt.suptitle(f'Combined Test Results Summary ({len(results)} Tests)', fontsize=16, fontweight='bold')

    # 1. MMSE Comparison (Bar Chart)
    ax1 = axes[0]
    bars = ax1.bar(names, mmses, color='skyblue', edgecolor='black', alpha=0.8)
    ax1.set_title('MMSE (Mean Squared Error) per Test Case', fontweight='bold')
    ax1.set_ylabel('MMSE Value')
    ax1.set_xlabel('Test Case ID')
    ax1.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)

    # 2. Error Distribution (Box Plot)
    ax2 = axes[1]
    # Boxplot expects a list of arrays
    ax2.boxplot(errors, labels=names, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', alpha=0.6),
                medianprops=dict(color='red'))
    
    ax2.set_title('Error Distribution Variance (Box Plot)', fontweight='bold')
    ax2.set_ylabel('Error Magnitude (Desired - Output)')
    ax2.set_xlabel('Test Case ID')
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save inside the tests/ folder
    save_path = os.path.join(TESTS_DIR, OUTPUT_FILENAME)
    plt.savefig(save_path, dpi=150)
    print(f"\n[Success] Combined graph saved to: {save_path}")

if __name__ == "__main__":
    data = collect_data()
    plot_combined_results(data)