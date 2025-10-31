# CO2011 - Symbolic and Algebraic Reasoning in Petri Nets

This project is an assignment for the CO2008 Computer Architecture Lab course at Ho Chi Minh City University of Technology.
It implements and tests the Wiener Filter for signal estimation using Python (high-level model) before translating the logic to MIPS Assembly.

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
    py test.py

## This script performs:

1. Generates a desired signal and two noise sources (white and colored).

2. Combines them into input test files:

    - desired.txt

    - noise_white.txt

    - noise_colored.txt

    - input_1.txt

    - input_2.txt
   
4. Computes:
   
    - Autocorrelation matrix `𝑅_𝑀`
   
    - Cross-correlation vector `𝛾𝑑`
   
    - Optimal coefficients `ℎ_𝑜𝑝𝑡`
  
    - Output signal `𝑦(𝑛)`
  
    - `MMSE` (Mean Minimum Square Error)

5. Writes the results to `output.txt`
   

	​
	​

	​
