# In case any input is invalid, return -1
import numpy as np

class HammingLSHFamily():
    _dim: int  # Dimension d of the Hamming space
    # TODO: add what you need here
    _i: int
    _hash_index: int

    def __init__(self, dimension: int):
        self._dim = dimension
        self.pick_hash()
        # TODO: Whatever else you need to initialise
        self._hash_index = 0
        

    def size(self) -> int:
        """
        Returns the number of hash functions in the family
        """
        # TODO: Implement this method.
        return self._dim

    def pick_hash(self):
        """
        Chooses a uniformly random hash function in the family (discarding)
        """
        # TODO: Implement this method.
        self._i = np.random.randint(0, self._dim-1)

    def hash(self, x: int) -> bool:
        """
        Returns the hash of the d-dimensional bit string x, according to the 
        currently chosen hash function. The input x is represented as an integer
        0 <= x <= 2^d - 1; the hash is a value 1 <= y <= d
        """
        # TODO: Implement this method.
        #return bool((x >> self._hash_index) & 1)
        return bool((x >> self._hash_index) & 1)
