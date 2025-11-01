#####################################################################
# MIPS IMPLEMENTATION OF A WIENER FILTER (FINAL VERSION)
#
# Reads from stdin (e.g., '... < input.txt')
# Writes to stdout (e.g., '... > output.txt')
#
# Fix: 
#   1. Initializes $f30 to 0.0 to prevent NaN.
#   2. Corrects output format to match assignment example
#      (space-separated floats, prefixed with "Filtered output:").
#
#####################################################################

.data
    # --- Constants ---
    N:              .word 500       # 500 sequences
    M:              .word 4         # 4 filter taps
    FLOAT_SIZE:     .word 4         # 4 bytes per float
    
    # --- String Literals ---
    str_filtered_out: .asciiz "Filtered output:\n" # *** NEW ***
    str_space:        .asciiz " "                  # *** NEW ***
    str_mmse_result:  .asciiz "\nMMSE: "           # *** MODIFIED ***
    str_newline:      .asciiz "\n"
    
    float_zero:     .float 0.0      # Define 0.0
    
    .align 4  # Align buffers to 4-byte boundary

    # --- Buffers (N=500, M=4) ---
    desired_signal_array: .space 2000
    input_signal_array:   .space 2000
    y_out_array:          .space 2000
    gamma_d_vector:       .space 16
    h_opt_vector:         .space 16
    gamma_xx_temp:        .space 16
    R_M_matrix:           .space 64
    aug_matrix:           .space 80


.text
.globl main
main:
    # Load constants
    lw $s0, N             # $s0 = N = 500
    lw $s1, M             # $s1 = M = 4
    lw $s2, FLOAT_SIZE    # $s2 = 4 (bytes)
    
    l.s $f30, float_zero  # Load 0.0 into $f30

    # --- Step 3: Load Data from stdin ---
    la $a0, desired_signal_array
    la $a1, input_signal_array
    move $a2, $s0         # N
    jal proc_read_stdin

    # --- Step 4: Calculate R_M ---
    la $a0, input_signal_array
    la $a1, R_M_matrix
    la $a2, gamma_xx_temp
    move $a3, $s0         # a3 = N
    
    addi $sp, $sp, -4
    sw $s1, 0($sp)        # Push M ($s1)
    jal proc_build_R_M
    addi $sp, $sp, 4      # Pop M
    

    # --- Step 5: Calculate gamma_d ---
    la $a0, desired_signal_array
    la $a1, input_signal_array
    la $a2, gamma_d_vector
    move $a3, $s0         # a3 = N

    addi $sp, $sp, -4
    sw $s1, 0($sp)        # Push M ($s1)
    jal proc_build_gamma_d
    addi $sp, $sp, 4      # Pop M

    # --- Step 6: Solve for h_opt ---
    la $a0, R_M_matrix
    la $a1, gamma_d_vector
    la $a2, h_opt_vector
    la $a3, aug_matrix    # a3 = scratchpad
    
    addi $sp, $sp, -4
    sw $s1, 0($sp)        # Push M ($s1)
    jal proc_solve_gaussian
    addi $sp, $sp, 4      # Pop M

    # --- Step 7: Apply Filter (Convolve) ---
    la $a0, input_signal_array
    la $a1, h_opt_vector
    la $a2, y_out_array
    move $a3, $s0         # a3 = N
    
    addi $sp, $sp, -4
    sw $s1, 0($sp)        # Push M ($s1)
    jal proc_convolve_same
    addi $sp, $sp, 4      # Pop M
    
    # --- Step 8: Calculate MMSE ---
    la $a0, desired_signal_array
    la $a1, y_out_array
    move $a2, $s0         # a2 = N
    jal proc_calc_mmse
    # MMSE result is in $f0

    # --- Step 9: Write Output to stdout ---
    la $a0, y_out_array
    move $a1, $s0         # N
    mov.s $f12, $f0       # $f12 = MMSE value
    jal proc_write_stdout
    
    jal proc_exit

#-------------------------------------------------------------------
# PROCEDURE: proc_read_stdin
# Reads N*2 floats from stdin using syscall 6.
#-------------------------------------------------------------------
proc_read_stdin:
    move $t0, $a0         # $t0 = &desired_signal_array
    move $t1, $a1         # $t1 = &input_signal_array
    move $t2, $a2         # $t2 = N
    li $t3, 0             # $t3 = i = 0
    li $t4, 4             # $t4 = 4 (bytes)

read_loop_1: # Read first N floats for desired_signal
    bge $t3, $t2, read_loop_2_start # if (i >= N), go to next loop
    
    li $v0, 6             # syscall 6: read float
    syscall               # Result is in $f0
    
    mul $t5, $t3, $t4     # $t5 = i * 4
    add $t6, $t0, $t5     # $t6 = &desired_signal_array[i]
    s.s $f0, 0($t6)       # store float
    
    addi $t3, $t3, 1      # i++
    j read_loop_1

read_loop_2_start:
    li $t3, 0             # $t3 = i = 0 (reset counter)

read_loop_2: # Read next N floats for input_signal
    bge $t3, $t2, read_end # if (i >= N), end
    
    li $v0, 6             # syscall 6: read float
    syscall               # Result is in $f0
    
    mul $t5, $t3, $t4     # $t5 = i * 4
    add $t6, $t1, $t5     # $t6 = &input_signal_array[i]
    s.s $f0, 0($t6)       # store float
    
    addi $t3, $t3, 1      # i++
    j read_loop_2

read_end:
    jr $ra
    
#-------------------------------------------------------------------
# PROCEDURE: proc_write_stdout
# Writes the 500-sequence output and MMSE to stdout.
# *** THIS PROCEDURE IS MODIFIED TO MATCH ASSIGNMENT FORMAT ***
#-------------------------------------------------------------------
proc_write_stdout:
    move $t0, $a0         # $t0 = &y_out_array
    move $t1, $a1         # $t1 = N
    li $t2, 0             # $t2 = i = 0
    li $t3, 4             # $t3 = 4 (bytes)

    # Print "Filtered output:" string FIRST
    li $v0, 4
    la $a0, str_filtered_out
    syscall

write_loop:
    bge $t2, $t1, write_mmse # if (i >= N), end loop
    
    # Get y_out[i]
    mul $t4, $t2, $t3
    add $t4, $t0, $t4     # $t4 = &y_out[i]
    l.s $f1, 0($t4)
    
    # Print float (to stdout)
    li $v0, 2
    mov.s $f12, $f1       # $f12 = float to print
    syscall
    
    # Print a SPACE, not a newline
    li $v0, 4
    la $a0, str_space
    syscall
    
    addi $t2, $t2, 1      # i++
    j write_loop

write_mmse:
    # Print "MMSE: " string
    # We add a newline BEFORE it, to separate it from the filter output
    li $v0, 4
    la $a0, str_mmse_result
    syscall
    
    # Print MMSE value (to stdout)
    li $v0, 2
    # $f12 already contains MMSE
    syscall
    
    jr $ra

#-------------------------------------------------------------------
# PROCEDURE: proc_calc_gamma_xx
#-------------------------------------------------------------------
proc_calc_gamma_xx:
    sub $t0, $a2, $a1     # $t0 = N - k (loop limit)
    li $t1, 0             # $t1 = n = 0
    mov.s $f0, $f30       # $f0 = sum = 0.0
gamma_xx_loop:
    bge $t1, $t0, gamma_xx_end
    add $t2, $t1, $a1
    mul $t3, $t1, 4
    add $t3, $a0, $t3
    l.s $f1, 0($t3)
    mul $t4, $t2, 4
    add $t4, $a0, $t4
    l.s $f2, 0($t4)
    mul.s $f3, $f1, $f2
    add.s $f0, $f0, $f3
    addi $t1, $t1, 1
    j gamma_xx_loop
gamma_xx_end:
    jr $ra
    
#-------------------------------------------------------------------
# PROCEDURE: proc_calc_gamma_dx
#-------------------------------------------------------------------
proc_calc_gamma_dx:
    sub $t0, $a3, $a2
    li $t1, 0
    mov.s $f0, $f30
gamma_dx_loop:
    bge $t1, $t0, gamma_dx_end
    add $t2, $t1, $a2
    mul $t3, $t1, 4
    add $t3, $a1, $t3
    l.s $f1, 0($t3)
    mul $t4, $t2, 4
    add $t4, $a0, $t4
    l.s $f2, 0($t4)
    mul.s $f3, $f1, $f2
    add.s $f0, $f0, $f3
    addi $t1, $t1, 1
    j gamma_dx_loop
gamma_dx_end:
    jr $ra
    
#-------------------------------------------------------------------
# PROCEDURE: proc_build_R_M
#-------------------------------------------------------------------
proc_build_R_M:
    addi $sp, $sp, -28
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)
    sw $s3, 16($sp)
    sw $s4, 20($sp)
    sw $s5, 24($sp)
    
    move $s0, $a0
    move $s1, $a1
    move $s2, $a2
    move $s3, $a3
    
    lw $s4, 28($sp)       # $s4 = M (Load 5th arg)
    li $t0, 0
build_R_M_loop1:
    bge $t0, $s4, build_R_M_loop1_end
    move $a0, $s0
    move $a1, $t0
    move $a2, $s3
    jal proc_calc_gamma_xx
    mul $t1, $t0, 4
    add $t1, $s2, $t1
    s.s $f0, 0($t1)
    addi $t0, $t0, 1
    j build_R_M_loop1
build_R_M_loop1_end:
    li $t0, 0
build_R_M_loop_l:
    bge $t0, $s4, build_R_M_loop_end
    li $t1, 0
build_R_M_loop_k:
    bge $t1, $s4, build_R_M_loop_l_inc
    sub $t2, $t0, $t1
    blt $t2, $zero, abs_neg
    move $t3, $t2
    j abs_done
abs_neg:
    sub $t3, $zero, $t2
abs_done:
    mul $t4, $t3, 4
    add $t4, $s2, $t4
    l.s $f1, 0($t4)
    mul $t5, $t0, $s4
    add $t5, $t5, $t1
    mul $t5, $t5, 4
    add $t5, $s1, $t5
    s.s $f1, 0($t5)
    addi $t1, $t1, 1
    j build_R_M_loop_k
build_R_M_loop_l_inc:
    addi $t0, $t0, 1
    j build_R_M_loop_l
build_R_M_loop_end:
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    lw $s3, 16($sp)
    lw $s4, 20($sp)
    lw $s5, 24($sp)
    addi $sp, $sp, 28
    jr $ra

#-------------------------------------------------------------------
# PROCEDURE: proc_build_gamma_d
#-------------------------------------------------------------------
proc_build_gamma_d:
    addi $sp, $sp, -24
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)
    sw $s3, 16($sp)
    sw $s4, 20($sp)

    move $s0, $a0
    move $s1, $a1
    move $s2, $a2
    move $s3, $a3
    
    lw $s4, 24($sp)       # $s4 = M (Load 5th arg)
    li $t0, 0
build_gamma_d_loop:
    bge $t0, $s4, build_gamma_d_end
    move $a0, $s0
    move $a1, $s1
    move $a2, $t0
    move $a3, $s3
    jal proc_calc_gamma_dx
    mul $t1, $t0, 4
    add $t1, $s2, $t1
    s.s $f0, 0($t1)
    addi $t0, $t0, 1
    j build_gamma_d_loop
build_gamma_d_end:
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    lw $s3, 16($sp)
    lw $s4, 20($sp)
    addi $sp, $sp, 24
    jr $ra

#-------------------------------------------------------------------
# PROCEDURE: proc_solve_gaussian
#-------------------------------------------------------------------
proc_solve_gaussian:
    addi $sp, $sp, -24
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)
    sw $s3, 16($sp)
    sw $s4, 20($sp)
    
    move $s0, $a0
    move $s1, $a1
    move $s2, $a2
    move $s3, $a3
    
    lw $s4, 24($sp)       # $s4 = M (Load 5th arg)
    li $t0, 5
    li $t1, 0
gauss_build_loop_i:
    bge $t1, $s4, gauss_build_end
    li $t2, 0
gauss_build_loop_j:
    bge $t2, $s4, gauss_build_col_M
    mul $t3, $t1, $s4
    add $t3, $t3, $t2
    mul $t3, $t3, 4
    add $t3, $s0, $t3
    l.s $f1, 0($t3)
    mul $t4, $t1, $t0
    add $t4, $t4, $t2
    mul $t4, $t4, 4
    add $t4, $s3, $t4
    s.s $f1, 0($t4)
    addi $t2, $t2, 1
    j gauss_build_loop_j
gauss_build_col_M:
    mul $t3, $t1, 4
    add $t3, $s1, $t3
    l.s $f1, 0($t3)
    mul $t4, $t1, $t0
    add $t4, $t4, $s4
    mul $t4, $t4, 4
    add $t4, $s3, $t4
    s.s $f1, 0($t4)
    addi $t1, $t1, 1
    j gauss_build_loop_i
gauss_build_end:
    li $t1, 0
gauss_fwd_loop_k:
    sub $t2, $s4, 1
    bge $t1, $t2, gauss_fwd_end
    addi $t2, $t1, 1
gauss_fwd_loop_i:
    bge $t2, $s4, gauss_fwd_k_inc
    mul $t3, $t2, $t0
    add $t3, $t3, $t1
    mul $t3, $t3, 4
    add $t3, $s3, $t3
    l.s $f1, 0($t3)
    mul $t4, $t1, $t0
    add $t4, $t4, $t1
    mul $t4, $t4, 4
    add $t4, $s3, $t4
    l.s $f2, 0($t4)
    div.s $f3, $f1, $f2
    move $t5, $t1
gauss_fwd_loop_j:
    bge $t5, $t0, gauss_fwd_i_inc
    mul $t6, $t1, $t0
    add $t6, $t6, $t5
    mul $t6, $t6, 4
    add $t6, $s3, $t6
    l.s $f4, 0($t6)
    mul $t7, $t2, $t0
    add $t7, $t7, $t5
    mul $t7, $t7, 4
    add $t7, $s3, $t7
    l.s $f5, 0($t7)
    mul.s $f6, $f3, $f4
    sub.s $f7, $f5, $f6
    s.s $f7, 0($t7)
    addi $t5, $t5, 1
    j gauss_fwd_loop_j
gauss_fwd_i_inc:
    addi $t2, $t2, 1
    j gauss_fwd_loop_i
gauss_fwd_k_inc:
    addi $t1, $t1, 1
    j gauss_fwd_loop_k
gauss_fwd_end:
    sub $t1, $s4, 1
gauss_back_loop_i:
    blt $t1, $zero, gauss_back_end
    mul $t2, $t1, $t0
    add $t2, $t2, $s4
    mul $t2, $t2, 4
    add $t2, $s3, $t2
    l.s $f1, 0($t2)
    addi $t3, $t1, 1
gauss_back_loop_j:
    bge $t3, $s4, gauss_back_calc_x
    mul $t4, $t1, $t0
    add $t4, $t4, $t3
    mul $t4, $t4, 4
    add $t4, $s3, $t4
    l.s $f2, 0($t4)
    mul $t5, $t3, 4
    add $t5, $s2, $t5
    l.s $f3, 0($t5)
    mul.s $f4, $f2, $f3
    sub.s $f1, $f1, $f4
    addi $t3, $t3, 1
    j gauss_back_loop_j
gauss_back_calc_x:
    mul $t6, $t1, $t0
    add $t6, $t6, $t1
    mul $t6, $t6, 4
    add $t6, $s3, $t6
    l.s $f5, 0($t6)
    div.s $f6, $f1, $f5
    mul $t7, $t1, 4
    add $t7, $s2, $t7
    s.s $f6, 0($t7)
    addi $t1, $t1, -1
    j gauss_back_loop_i
gauss_back_end:
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    lw $s3, 16($sp)
    lw $s4, 20($sp)
    addi $sp, $sp, 24
    jr $ra

#-------------------------------------------------------------------
# PROCEDURE: proc_convolve_same
#-------------------------------------------------------------------
proc_convolve_same:
    addi $sp, $sp, -24
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)
    sw $s3, 16($sp)
    sw $s4, 20($sp)
    
    move $s0, $a0
    move $s1, $a1
    move $s2, $a2
    move $s3, $a3
    
    lw $s4, 24($sp)       # $s4 = M (Load 5th arg)
    li $t0, 0
conv_loop_n:
    bge $t0, $s3, conv_end
    mov.s $f0, $f30
    li $t1, 0
conv_loop_k:
    bge $t1, $s4, conv_n_store
    sub $t2, $t0, $t1
    blt $t2, $zero, conv_k_inc
    mul $t3, $t1, 4
    add $t3, $s1, $t3
    l.s $f1, 0($t3)
    mul $t4, $t2, 4
    add $t4, $s0, $t4
    l.s $f2, 0($t4)
    mul.s $f3, $f1, $f2
    add.s $f0, $f0, $f3
conv_k_inc:
    addi $t1, $t1, 1
    j conv_loop_k
conv_n_store:
    mul $t5, $t0, 4
    add $t5, $s2, $t5
    s.s $f0, 0($t5)
    addi $t0, $t0, 1
    j conv_loop_n
conv_end:
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    lw $s3, 16($sp)
    lw $s4, 20($sp)
    addi $sp, $sp, 24
    jr $ra

#-------------------------------------------------------------------
# PROCEDURE: proc_calc_mmse
#-------------------------------------------------------------------
proc_calc_mmse:
    addi $sp, $sp, -16
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)

    move $s0, $a0
    move $s1, $a1
    move $s2, $a2
    
    li $t0, 0
    mov.s $f0, $f30
mmse_loop:
    bge $t0, $s2, mmse_calc_mean
    mul $t1, $t0, 4
    add $t2, $s0, $t1
    add $t3, $s1, $t1
    l.s $f1, 0($t2)
    l.s $f2, 0($t3)
    sub.s $f3, $f1, $f2
    mul.s $f4, $f3, $f3
    add.s $f0, $f0, $f4
    addi $t0, $t0, 1
    j mmse_loop
mmse_calc_mean:
    mtc1 $s2, $f1
    cvt.s.w $f1, $f1
    div.s $f0, $f0, $f1
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    addi $sp, $sp, 16
    jr $ra
    
#-------------------------------------------------------------------
# PROCEDURE: proc_exit
#-------------------------------------------------------------------
proc_exit:
    li $v0, 10
    syscall