from typing import List, Optional, Tuple
import numpy as np
import math
from lshfamily import HammingLSHFamily
from hashtable import SeparateChaining

"""
BabyANN for Hamming distance
----------
This class implements the "Baby LSH" data structure for ANN. For more details, consult the lecture on LSH.

d-dimensional inputs (d-bit strings) are represented as integers taking value 
0 <= x <= 2^d-1

The following functions are available:
    - preprocess: preprocess a dataset of (at most) n data points, each being a d-bit string
    - query: given a d-bit string x, return an element y in S, or None, satisfying the
        guarantees of the "baby ANN" data structure seen in the lecture
    - dist: returns the Hamming distance between two points
"""


class BabyANN():
    _c: float # Must have C>1. Check this!
    _r: float # Must have r>0
    # TODO: anything else you need.

    def __init__(self, dimension: int, radius: float, C: float, n: int):
        """
        Constructor for the data structure. 
        Initializes the map with the given capacity.

        :param dimension: the dimension d of the Hamming space
        :param radius: The radius 0 < r < d
        :param C: The approximation parameter C > 1
        :param n: The number of datapoints n supported by the data structure
        """
        # TODO: Implement this method.
        if C <= 1:
            return None
        if radius <= 0 or radius >= dimension:
            return None
        self.dimension = dimension
        self.radius = radius
        self.C = C
        self.n = n
        
        #p,q calculation
        self.p = 1 - radius/dimension
        self.q = 1 - (C*radius)/dimension
        
        #rho value
        self.rho = math.log(1/self.p)/math.log(1/self.q)
        
        self.l = math.ceil(math.log(n) / math.log(1 / self.q))
        self.k = math.ceil(math.log(10) / math.log(1 / (1 - self.p**self.l)))
        
        '''
        self.l = math.ceil(math.log(n) / math.log(1 / self.q))
        self.k = math.ceil(math.log(10) / math.log(1 / (1 - self.p**self.l)))
        '''


        #self.hash_tables = [SeparateChaining(n) for i in range(self.k)]
        
        # OPTIMIZATION: Reduced number of hash functions per table
        # Balancing between performance and accuracy
        #self.l = max(1, min(3, math.ceil(math.log(n) / math.log(1 / self.q)))) #3 bits only
        
        # OPTIMIZATION: Reduced number of hash tables
        # Less tables means faster processing with slight accuracy tradeoff
        #self.k = max(1, min(5, math.ceil(math.log(5) / math.log(1 / (1 - self.p**self.l))))) #3 bits only
        #self.l = math.ceil(math.log(n) / math.log(1 / self.q))


        '''
        
        #almost optimized version
        self.l = max(1, min(int(3 * math.log(n,2)), math.ceil(math.log(n) / math.log(1 / self.q))))
        self.k = max(1, min(10, math.ceil(math.log(5) / math.log(1 / (1 - self.p**self.l)))))
        '''

        # Create hash tables with appropriate sizing
        self.hash_tables = [SeparateChaining(max(n//2, 10)) for i in range(self.k)]
        

        #creating l hash functions
        self.lsh_functions = []
        for i in range(self.k):
            functions = []
            for z in range(self.l):
                lsh = HammingLSHFamily(dimension)
                functions.append(lsh)
            self.lsh_functions.append(functions)

        self.dataset = []

    def preprocess(self, dataset: List[int]) -> None:
        """
        Preprocess the dataset S

        :param dataset: a dataset S of at most n d-bit strings
        """
        # TODO: Implement this method.
        
        if len(dataset) > self.n:
            raise ValueError(f"Dataset size exceeds capacity: {len(dataset)} > {self.n}")
        
        # Store the dataset
        self.dataset = dataset
        
        # Insert all data points into all k hash tables
        for x in dataset:
            for t in range(self.k):
                # Hash x using the l LSH functions for table t
                hash_key = self.compute_hash_key(x, t)
                
                # Insert x into the t-th hash table
                self.hash_tables[t].put(hash_key, x)


    def query(self, x: int) -> None:
        """
        Given a d-bit string x (represented as an integer), return an element y in S, or None, satisfying the
        guarantees of the "baby ANN" data structure seen in the lecture

        :param x: the query point
        :return: either an element of the dataset, or None
        """

        # TODO: Implement this method.
        
        for t in range(self.k):
            hash_key = self.compute_hash_key(x, t)
            bucket = self.hash_tables[t].get(hash_key)
            
            if bucket is not None:
                if self.dist(x, bucket) <= self.C * self.radius:
                    return bucket
        
        return None
    

    def dist(self, x: int, y:int) -> int:
        """
        Returns the Hamming distance between x and y, both represented as integers

        :param x: a d-bit string represented as an integer
        :param y: a d-bit string represented as an integer
        :return: The Hamming distance between x and y
        """

        # TODO: Implement this method.
        xor_result = x ^ y
        distance = 0
        
        while xor_result > 0:
            distance += xor_result & 1
            # Shift right by 1
            xor_result >>= 1
        
        return distance
    
    def compute_hash_key(self, x: int, table_idx: int) -> int:
        """
        Computes the hash key for an element x for the specified hash table
        
        :param x: the element to hash
        :param table_idx: the index of the hash table
        :return: the hash key
        """
        # Combine the l hash values into a single key
        hash_key = 0
        
        for i in range(self.l):
            # Get the i-th LSH hash value
            bit = self.lsh_functions[table_idx][i].hash(x)
            
            # Set the i-th bit of the hash key
            hash_key |= (int(bit) << i)
        
        return hash_key

    

