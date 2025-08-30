import numpy as np
import matplotlib.pyplot as plt
import time
from typing import List, Tuple
from ann import BabyANN

def generate_dataset(d: int) -> List[int]:
    """
    Generate a dataset consisting of all d-bit strings with exactly 2 or 3 bits set to 1.
    
    :param d: dimension
    :return: list of integers representing the dataset
    """
    dataset = []
    
    # Add all strings with exactly 2 bits set to 1
    for i in range(d):
        for j in range(i+1, d):
            # Set bits i and j to 1
            x = (1 << i) | (1 << j)
            dataset.append(x)
    
    # Add all strings with exactly 3 bits set to 1
    for i in range(d):
        for j in range(i+1, d):
            for k in range(j+1, d):
                # Set bits i, j, and k to 1
                x = (1 << i) | (1 << j) | (1 << k)
                dataset.append(x)
    
    return dataset

def generate_queries(d: int) -> List[int]:
    """
    Generate queries consisting of all d-bit strings with exactly 1 bit set to 1.
    
    :param d: dimension
    :return: list of integers representing the queries
    """
    queries = []
    for i in range(d):
        # Set bit i to 1
        x = 1 << i
        queries.append(x)
    return queries

def evaluate_babyann(d: int, n: int, r_values: List[float], C_values: List[float]) -> Tuple[dict, dict]:
    """
    Evaluate the BabyANN data structure for different values of r and C.
    
    :param d: dimension
    :param n: size of the dataset
    :param r_values: list of radius values
    :param C_values: list of approximation parameter values
    :return: tuple of dictionaries containing query times and results
    """
    dataset = generate_dataset(d)
    queries = generate_queries(d)
    
    # Sanity check
    assert len(dataset) == n, f"Generated dataset size {len(dataset)} does not match expected size {n}"
    
    query_times = {}  # (r, C) -> average query time
    query_results = {}  # (r, C) -> list of query results
    
    for r in r_values:
        for C in C_values:
            print(f"Evaluating BabyANN with r={r}, C={C}")
            
            # Initialize and preprocess
            ann = BabyANN(d, r, C, n)
            ann.preprocess(dataset)
            
            # Evaluate queries
            start_time = time.time()
            results = []
            
            for query in queries:
                result = ann.query(query)
                if result is not None:
                    dist = ann.dist(query, result)
                    shared = [i for i in range(d) if ((query >> i) & 1) and ((result >> i) & 1)]
                    print(f"Query: {bin(query)}, Match: {bin(result)}, Distance: {dist}, Shared bits: {shared}  success")
                    results.append(dist)
                else:
                    results.append(None)
                    
            end_time = time.time()
            avg_time = (end_time - start_time) / len(queries)
            
            # Store results
            query_times[(r, C)] = avg_time
            query_results[(r, C)] = results
            
            print(f"  Average query time: {avg_time:.6f} seconds")
            print(f"  Number of None results: {results.count(None)}")
            if results.count(None) < len(results):
                print(f"  Average distance (excluding None): {np.mean([d for d in results if d is not None]):.2f}")
            
    return query_times, query_results

def plot_results(d: int, r_values: List[float], C_values: List[float], 
                 query_times: dict, query_results: dict) -> None:
    """
    Plot the evaluation results.
    
    :param d: dimension
    :param r_values: list of radius values
    :param C_values: list of approximation parameter values
    :param query_times: dictionary of query times
    :param query_results: dictionary of query results
    """
    # Plot 1: Average query time as a function of C, for each value of r
    plt.figure(figsize=(10, 6))
    
    for r in r_values:
        times = [query_times[(r, C)] for C in C_values]
        plt.plot(C_values, times, marker='o', label=f'r={r}')
    
    plt.xlabel('C (Approximation factor)')
    plt.ylabel('Average query time (seconds)')
    plt.title('Average query time as a function of C')
    plt.legend()
    plt.grid(True)
    plt.savefig('query_times.png')
    
    # Plot 2: Histograms of query answers
    fig, axs = plt.subplots(len(r_values), len(C_values), figsize=(15, 10))
    
    for i, r in enumerate(r_values):
        for j, C in enumerate(C_values):
            ax = axs[i, j]
            results = query_results[(r, C)]
            
            # Filter out None values
            valid_results = [res for res in results if res is not None]
            
            if valid_results:
                # Create bins for the histogram
                max_dist = max(valid_results)
                bins = np.arange(0, max_dist + 2) - 0.5
                
                ax.hist(valid_results, bins=bins, alpha=0.7)
                ax.set_title(f'r={r}, C={C}')
                ax.set_xlabel('Distance')
                ax.set_ylabel('Count')
                
                # Add count of None results
                none_count = results.count(None)
                if none_count > 0:
                    ax.text(0.5, 0.9, f'None: {none_count}', 
                           transform=ax.transAxes, ha='center')
            else:
                ax.text(0.5, 0.5, f'All queries returned None', 
                       transform=ax.transAxes, ha='center')
    
    plt.tight_layout()
    plt.savefig('query_results_histogram.png')
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print("------------------")
    for r in r_values:
        for C in C_values:
            results = query_results[(r, C)]
            valid_results = [res for res in results if res is not None]
            
            print(f"r={r}, C={C}:")
            print(f"  Query time: {query_times[(r, C)]:.6f} seconds")
            print(f"  None results: {results.count(None)}/{len(results)}")
            
            if valid_results:
                print(f"  Min distance: {min(valid_results)}")
                print(f"  Max distance: {max(valid_results)}")
                print(f"  Mean distance: {np.mean(valid_results):.2f}")
                print(f"  Median distance: {np.median(valid_results)}")
            print()

def main():
    # Set parameters
    d = 40
    n = (d * (d - 1) // 2) + (d * (d - 1) * (d - 2) // 6)  # Combination formula for "2 choose from d" + "3 choose from d"
    print(f"Dimension d: {d}")
    print(f"Dataset size n: {n}")
    
    r_values = [0.5, 1, 1.5, 2]
    C_values = [1.25, 1.5, 1.75, 2]
    
    # Run evaluation
    query_times, query_results = evaluate_babyann(d, n, r_values, C_values)
    
    # Plot results
    plot_results(d, r_values, C_values, query_times, query_results)
    
    print("Evaluation complete. Results saved to 'query_times.png' and 'query_results_histogram.png'.")

if __name__ == "__main__":
    main()
