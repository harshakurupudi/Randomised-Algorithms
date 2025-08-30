import numpy as np
import matplotlib.pyplot as plt
import time
from typing import List, Tuple, Dict

class LSHParameterDebugger:
    """
    Tool to analyze and visualize how LSH parameters change with different radius values
    """
    
    @staticmethod
    def calculate_parameters(d: int, n: int, r_values: List[float], C_values: List[float]) -> Dict:
        """
        Calculate l and k parameters for different r and C values
        """
        results = {}
        
        for r in r_values:
            for C in C_values:
                # Calculate p and q
                p = 1 - r/d
                q = 1 - (C*r)/d
                
                # Calculate theoretical l and k
                theoretical_l = np.ceil(np.log(n) / np.log(1 / q))
                
                # Calculate practical l (using 3*log2(d) constraint)
                practical_l = int(3 * np.log2(d))
                actual_l = max(1, min(practical_l, theoretical_l))
                
                # Calculate k based on actual l
                p_to_l = p**actual_l
                theoretical_k = np.ceil(np.log(5) / np.log(1 / (1 - p_to_l)))
                actual_k = max(1, min(10, theoretical_k))
                
                # Calculate rho value
                rho = np.log(1/p) / np.log(1/q)
                
                # Store results
                key = (r, C)
                results[key] = {
                    'p': p,
                    'q': q,
                    'theoretical_l': theoretical_l,
                    'practical_l': practical_l,
                    'actual_l': actual_l,
                    'p_to_l': p_to_l,
                    'theoretical_k': theoretical_k,
                    'actual_k': actual_k,
                    'rho': rho,
                    'estimated_complexity': n**(1 + rho),
                    'estimated_buckets': n * (1 - (1-q**actual_l)**actual_k)
                }
        
        return results
    
    @staticmethod
    def visualize_parameters(results: Dict):
        """
        Visualize how parameters change with r and C values
        """
        r_values = sorted(set(key[0] for key in results.keys()))
        C_values = sorted(set(key[1] for key in results.keys()))
        
        # Set up subplots
        fig, axs = plt.subplots(2, 3, figsize=(18, 12))
        
        # Plot 1: l values
        for C in C_values:
            l_values = [results[(r, C)]['actual_l'] for r in r_values]
            axs[0, 0].plot(r_values, l_values, marker='o', label=f'C={C}')
        
        axs[0, 0].set_xlabel('Radius (r)')
        axs[0, 0].set_ylabel('Number of hash functions (l)')
        axs[0, 0].set_title('l vs. r')
        axs[0, 0].legend()
        axs[0, 0].grid(True)
        
        # Plot 2: k values
        for C in C_values:
            k_values = [results[(r, C)]['actual_k'] for r in r_values]
            axs[0, 1].plot(r_values, k_values, marker='o', label=f'C={C}')
        
        axs[0, 1].set_xlabel('Radius (r)')
        axs[0, 1].set_ylabel('Number of hash tables (k)')
        axs[0, 1].set_title('k vs. r')
        axs[0, 1].legend()
        axs[0, 1].grid(True)
        
        # Plot 3: rho values
        for C in C_values:
            rho_values = [results[(r, C)]['rho'] for r in r_values]
            axs[0, 2].plot(r_values, rho_values, marker='o', label=f'C={C}')
        
        axs[0, 2].set_xlabel('Radius (r)')
        axs[0, 2].set_ylabel('rho value')
        axs[0, 2].set_title('rho vs. r')
        axs[0, 2].legend()
        axs[0, 2].grid(True)
        
        # Plot 4: p and q values
        for C in C_values:
            p_values = [results[(r, C)]['p'] for r in r_values]
            q_values = [results[(r, C)]['q'] for r in r_values]
            axs[1, 0].plot(r_values, p_values, marker='o', linestyle='-', label=f'p (C={C})')
            axs[1, 0].plot(r_values, q_values, marker='x', linestyle='--', label=f'q (C={C})')
        
        axs[1, 0].set_xlabel('Radius (r)')
        axs[1, 0].set_ylabel('Collision probabilities')
        axs[1, 0].set_title('p and q vs. r')
        axs[1, 0].legend()
        axs[1, 0].grid(True)
        
        # Plot 5: Estimated complexity
        for C in C_values:
            complexity = [results[(r, C)]['estimated_complexity'] for r in r_values]
            # Use log scale for complexity
            axs[1, 1].plot(r_values, np.log10(complexity), marker='o', label=f'C={C}')
        
        axs[1, 1].set_xlabel('Radius (r)')
        axs[1, 1].set_ylabel('Log10(estimated complexity)')
        axs[1, 1].set_title('Estimated complexity vs. r')
        axs[1, 1].legend()
        axs[1, 1].grid(True)
        
        # Plot 6: Estimated bucket counts
        for C in C_values:
            bucket_estimates = [results[(r, C)]['estimated_buckets'] for r in r_values]
            axs[1, 2].plot(r_values, bucket_estimates, marker='o', label=f'C={C}')
        
        axs[1, 2].set_xlabel('Radius (r)')
        axs[1, 2].set_ylabel('Est. buckets searched per query')
        axs[1, 2].set_title('Estimated buckets vs. r')
        axs[1, 2].legend()
        axs[1, 2].grid(True)
        
        plt.tight_layout()
        plt.savefig('lsh_parameter_analysis.png')
        print("Analysis saved to 'lsh_parameter_analysis.png'")
        
        # Print detailed parameter table
        print("\nDetailed Parameter Table:")
        print("========================")
        print(f"{'r':>5} {'C':>5} {'l':>5} {'k':>5} {'p':>8} {'q':>8} {'rho':>8}")
        print("-" * 50)
        
        for r in r_values:
            for C in C_values:
                params = results[(r, C)]
                print(f"{r:5.2f} {C:5.2f} {params['actual_l']:5d} {params['actual_k']:5d} "
                      f"{params['p']:8.4f} {params['q']:8.4f} {params['rho']:8.4f}")


def analyze_bucket_distribution(d: int, n: int, r: float, C: float):
    """
    Analyze the expected distribution of points in buckets
    """
    # Calculate parameters
    p = 1 - r/d
    q = 1 - (C*r)/d
    
    # Use constrained l value
    theoretical_l = np.ceil(np.log(n) / np.log(1 / q))
    practical_l = int(3 * np.log2(d))
    actual_l = max(1, min(practical_l, theoretical_l))
    
    # Estimate bucket distribution
    print(f"\nBucket Distribution Analysis for r={r}, C={C}:")
    print(f"Actual l value: {actual_l}")
    
    # Expected bucket size for a random point (using q^l collision probability)
    expected_collisions = n * q**actual_l
    print(f"Expected points per bucket: {expected_collisions:.2f}")
    
    # Probability distribution of bucket sizes
    bucket_capacities = range(0, 21)  # 0 to 20 points per bucket
    probabilities = []
    
    for size in bucket_capacities:
        if size == 0:
            # Probability of empty bucket
            prob = (1 - q**actual_l)**n
        else:
            # Binomial probability of exactly 'size' points in a bucket
            # This is an approximation for illustration
            prob = (math.comb(n, size)) * (q**actual_l)**size * (1-q**actual_l)**(n-size)
            # For numerical stability with large n
            from scipy.special import comb
            prob = comb(n, size) * (q**actual_l)**size * (1-q**actual_l)**(n-size)
        
        probabilities.append(prob)
        print(f"Probability of bucket with {size} points: {prob:.4e}")
    
    # Plot distribution
    plt.figure(figsize=(10, 6))
    plt.bar(bucket_capacities, probabilities)
    plt.xlabel('Number of points in bucket')
    plt.ylabel('Probability')
    plt.title(f'Expected Bucket Size Distribution (r={r}, C={C}, l={actual_l})')
    plt.yscale('log')  # Log scale for better visualization
    plt.grid(True, alpha=0.3)
    plt.savefig(f'bucket_distribution_r{r}_C{C}.png')


if __name__ == "__main__":
    # Set parameters
    d = 100
    n = (d * (d - 1) // 2) + (d * (d - 1) * (d - 2) // 6)
    print(f"Dimension d: {d}")
    print(f"Dataset size n: {n}")
    
    r_values = [0.5, 1, 1.5, 2]
    C_values = [1.25, 1.5, 1.75, 2]
    
    # Calculate and visualize parameters
    debugger = LSHParameterDebugger()
    results = debugger.calculate_parameters(d, n, r_values, C_values)
    debugger.visualize_parameters(results)
    
    # Analyze bucket distribution for specific cases
    for r in [0.5, 2.0]:
        analyze_bucket_distribution(d, n, r, 2.0)