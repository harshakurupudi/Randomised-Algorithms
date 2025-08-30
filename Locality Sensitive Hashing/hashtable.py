from typing import Generic, List, TypeVar, Tuple
from numpy import random


T = TypeVar('T')

"""
Hash table - Separate Chaining
----------

This class implements a hash table using separate chaining.
Recall that separate chaining is a method of storing data in a hash table where 
each cell of the table consists of a list of entries with an identical hashed key.
For more details, consult the lecture on hashing.

Keys are guaranteed to be integers while values can be of any arbitrary specified type.

The following functions are available:
    - hash: Hashes a given key to an index in the range [0, capacity)
    - put: Inserts a key-value pair into the hash table
    - get: Retrieves the value associated with a given key
    - remove: Removes a key-value pair from the hash table
    - size: Returns the number of key-value pairs in the hash table
    - capacity: Returns the capacity of the hash table
    - is_empty: Checks if the hash table is empty
    - entries: Returns a list of all key-value pairs in the hash table
"""


class SeparateChaining(Generic[T]):
    _size: int  # The number of key-value pairs in the map.
    _capacity: int  # The maximum size of the underlying table
    _table: List[List[Tuple[int, T]]]  # The underlying table with the entries

    def __init__(self, capacity: int):
        """
        Constructor for the hashmap. 
        Initializes the map with the given capacity.

        :param capacity: The capacity of the hashmap.
        """
        self._size = 0
        self._capacity = capacity
        # hash function parameters; should be integers
        # satisfying 
        # p: prime number greater than m (universe size)
        # a: randomly chosen integer with 1 <= a <= p-1
        # b: randomly chosen integer with 0 <= a <= p-1
        p = 1271293; # Hardcoded
        (a,b) = (random.randint(1,p),random.randint(0,p))
        self.hashparams = (a,b,p)

        # Fill the table with empty lists of the given capacity.
        self._table = [[] for i in range(capacity)]

    def hash(self, key: int) -> int:
        """
        Hashes a key to an index in the table.

        Note, you should call this function in your put, get and remove method
        rather than using the key value directly. This is to ensure that the key
        value is always an integer between 0 <= hash(key) < capacity.

        This function is provided for you. DO NOT EDIT IT.

        :param key: The key to hash.
        :return: The index in the table.
        """
        return ((self.hashparams[0]*key+self.hashparams[1]) % self.hashparams[2]) % self._capacity

    def put(self, key: int, value: T) -> None:
        """
        Puts a key-value pair in the hashmap.
        If the key already exists, the value is updated and the old value is returned.
        Otherwise, the value is inserted into the map and None is returned.

        :param key: The key to put.
        :param value: The value to put.
        """
        hash = self.hash(key)

        # If the key is already in the map, replace the value.
        for i in range(len(self._table[hash])):
            if self._table[hash][i][0] == key:
                old_value = self._table[hash][i][1]
                self._table[hash][i] = (key, value)
                return old_value

        # Otherwise, add the key-value pair to the list.
        self._table[hash].append((key, value))
        self._size += 1

    def get(self, key: int) -> T:
        """
        Gets the value associated with the given key.
        If the key does not exist, None is returned.
        Otherwise, returns the value associated with the key.

        :param key: The key to get.
        :return: The value associated with the key or None.
        """
        hash = self.hash(key)

        # Search for the key in the list.
        for i in range(len(self._table[hash])):
            if self._table[hash][i][0] == key:
                return self._table[hash][i][1]

        # If the key is not in the list, return None.
        return None

    def remove(self, key: int) -> T:
        """
        Removes the key-value pair associated with the given key.
        If the key does not exist, None is returned.
        Otherwise, returns the value associated with the key.

        :param key: The key to remove.
        :return: The value associated with the key or None.
        """
        hash = self.hash(key)

        # Search for the key in the list.
        for i in range(len(self._table[hash])):
            if self._table[hash][i][0] == key:
                old_value = self._table[hash][i][1]
                self._table[hash].pop(i)
                self._size -= 1
                return old_value

        # If the key is not in the list, return None.
        return None

    def size(self) -> int:
        """
        Returns the number of key-value pairs in the map.

        :return: The number of key-value pairs in the map.
        """
        return self._size

    def capacity(self) -> int:
        """
        Returns the capacity of the map.

        :return: The capacity of the map.
        """
        return self._capacity

    def is_empty(self) -> bool:
        """
        Returns True if the map is empty.

        :return: Boolean indicating if the map is empty.
        """
        return self._size == 0

    def entries(self) -> List[Tuple[int, T]]:
        """
        Returns a list of all key-value pairs in the map.

        :return: A list of all key-value pairs in the map.
        """
        entries = []

        # Iterate over the table and add all key-value pairs to the list.
        for i in range(self._capacity):
            for j in range(len(self._table[i])):
                entries.append(self._table[i][j])

        return entries
