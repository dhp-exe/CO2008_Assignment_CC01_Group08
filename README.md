# CO2008 - Wiener Filter Implementation

This project is an assignment for the **CO2008 Computer Architecture Lab** course at Ho Chi Minh City University of Technology. 
It implements the Wiener Filter for signal estimation using **Python** (as a high-level verification model) and **MIPS Assembly**.

## 📂 Project Structure

```text
.
├── main.asm           # MIPS Assembly implementation of the Wiener Filter
├── test.py            # Python script to run batch tests across all folders
├── plot.py            # Python script to visualize results (signals, error, FFT)
├── Mars4_5.jar        # MIPS Assembler and Runtime Simulator
└── tests/             # Test cases directory
    ├── test_001/      # Individual test case
    │   ├── input.txt    # Noisy input signal
    │   ├── desired.txt  # Original desired signal
    │   └── expected.txt # Expected output (for verification)
    ├── test_002/
    └── ...
```
## 📦 Setup

1.  Clone the repository:
    ```bash
    git clone ...
    cd CO2008_Assignment_CC01_Group08/
    ```

2.  Install the required Python libraries:
    ```bash
    pip install numpy
    ```

## 🚀 Running the Analysis
```bash
    py test.py
```
