import numpy as np
import math
import matplotlib.pyplot as plt
import sys
import random

def get_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_size(k, seen) + get_size(v, seen) for k, v in obj.items())
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_size(i, seen) for i in obj)
    return size

stream_values = []
with open("stream.txt", "r") as f:
    for line in f:
        elements = line.strip().split()
        if len(elements) == 2:
            try:
                val = int(elements[1])
                stream_values.append(val)
            except:
                continue
        if len(stream_values) >= 10000:
            break

def hash(a, b, x, p):
    return (b + a * x) % p

class Tidemark:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
        self.z = 0

    def h(self, x):
        return hash(self.a, self.b, x, self.p)

    def count_zeroes(self, x):
        return len(bin(x)) - len(bin(x).rstrip('0'))

    def Process(self, x):
        hz = self.count_zeroes(self.h(x))
        if hz > self.z:
            self.z = hz

    def Count(self):
        return (2**0.5) * (2 ** self.z)

    def Size(self):
        return get_size(self)

class BJKST:
    def __init__(self, a_h, b_h, a_g, p, k, T):
        self.a_h = a_h
        self.a_g = a_g
        self.b_h = b_h
        self.p = p
        self.k = k
        self.T = T
        self.z = 0
        self.B = set()

    def h(self, x):
        return hash(self.a_h, self.b_h, x, self.p)

    def g(self, x):
        return hash(self.a_g, self.b_h, x, self.p) % self.k

    def count_zeroes(self, x):
        return len(bin(x)) - len(bin(x).rstrip('0'))

    def Process(self, x):
        hz = self.count_zeroes(self.h(x))
        if hz >= self.z:
            self.B.add((self.g(x), hz))
        while len(self.B) >= self.T:
            self.z += 1
            self.B = {(gx, zx) for (gx, zx) in self.B if zx >= self.z}

    def Count(self):
        return len(self.B) * (2 ** self.z)

    def Size(self):
        return get_size(self)
def get_random_prime_between(n, m, max_attempts=10000):
    for _ in range(max_attempts):
        x = random.randint(n, m)
        if is_prime(x):
            return x
    raise ValueError("No prime found")

def is_prime(x):
    if x < 2: return False
    if x == 2: return True
    if x % 2 == 0: return False
    for i in range(3, int(x**0.5) + 1, 2):
        if x % i == 0: return False
    return True

primes = [104729, 1299709, 15485863]
epsilon = 0.2
results = {}
print ("Actual number of distinct values ", len(set(stream_values)))
for mod in primes:
    stream_mod = [x % mod for x in stream_values]
    a_tid = get_random_prime_between(1, mod - 1)
    a_h = random.randint(1, mod - 1)
    b_h = random.randint(1, mod - 1)
    a_g = random.randint(1, mod - 1)
    k = int((math.log2(len(set(stream_values))))**2 / (epsilon ** 4)*2/3)
    T = int(1 / (epsilon ** 2))
    print("Prime number ", mod)
    print("k ",k)
    print("T ", T)
    print("epsilon ", epsilon)

    tidemark = Tidemark(a_h, b_h, mod)
    bjkst = BJKST(a_h, b_h, a_g, mod, k, T)

    true_distinct = []
    tidemark_estimates = []
    bjkst_estimates = []
    #true_distinct = (set(stream_values))

    seen = set()

    for x in stream_mod:
        seen.add(x)
        tidemark.Process(x)
        bjkst.Process(x)
        true_distinct.append(len(seen))
        tidemark_estimates.append(tidemark.Count())
        bjkst_estimates.append(bjkst.Count())

    results[mod] = {
        "true": true_distinct,
        "tidemark": tidemark_estimates,
        "bjkst": bjkst_estimates
    }

    print(f"\nPrime {mod}")
    print("Tidemark: Count =", round(tidemark.Count()), "z =", tidemark.z, "Size =", tidemark.Size())
    print("BJKST:    Count =", round(bjkst.Count()), "z =", bjkst.z, "|B| =", len(bjkst.B), "Size =", bjkst.Size())
    #print("True distinct elements:", len(seen))

    ks = list(range(1, len(results[mod]["true"]) + 1))

    plt.figure(figsize=(10, 6))
    plt.plot(ks, results[mod]["true"], label="Actual distinct count")
    plt.plot(ks, results[mod]["tidemark"], label="Tidemark estimate")
    plt.plot(ks, results[mod]["bjkst"], label="BJKST estimate")
    plt.title(f"Tidemark vs BJKST Estimation (mod {mod})")
    plt.xlabel("Elements Processed")
    plt.ylabel("Estimated Count")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    mem_bjkst = BJKST(a_h, a_g, b_h, mod, k, T)
    mem_tidemark = Tidemark(a_h, b_h, mod)
    s_stars_bjkst = []
    s_stars_tidemark = []

    for x in stream_mod:
        mem_bjkst.Process(x)
        s_stars_bjkst.append(mem_bjkst.Size())

        mem_tidemark.Process(x)
        s_stars_tidemark.append(mem_tidemark.Size())

    plt.figure(figsize=(10, 5))
    plt.plot(ks, s_stars_bjkst, label='BJKST memory (bytes)')
    plt.plot(ks, s_stars_tidemark, label='Tidemark memory (bytes)')
    plt.xlabel("Elements Processed")
    plt.ylabel("Memory Usage (bytes)")
    plt.title(f"Memory Usage: Tidemark vs BJKST (mod {mod})")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()