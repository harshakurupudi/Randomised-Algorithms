import matplotlib.pyplot as plt
import sys
import random

def is_prime(x):
    if x < 2: return False
    if x == 2: return True
    if x % 2 == 0: return False
    for i in range(3, int(x**0.5) + 1, 2):
        if x % i == 0: return False
    return True

def get_random_prime_between(n, m, max_attempts=10000):
    for _ in range(max_attempts):
        x = random.randint(n, m)
        if is_prime(x):
            return x
    raise ValueError(f"No prime found in {max_attempts} tries between {n} and {m}")

def simple_hash(a, k, p):
    return (a * k) % p

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

class Tidemark:
    def __init__(self, a, p):
        self.a = a
        self.p = p
        self.z = 0

    def count_zeroes(self, x):
        return len(bin(x)) - len(bin(x).rstrip('0'))

    def Process(self, x):
        hz = self.count_zeroes(x)
        if hz > self.z:
            self.z = hz

    def Count(self):
        return (2**(1/2)) * (2 ** self.z)

    def Size(self):
        return get_size(self)

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

p = get_random_prime_between(10001, 20000)
a = get_random_prime_between(2, p)
tidemark = Tidemark(a, p)

ks = []
sizes = []
zs = []

for k, val in enumerate(stream_values, start=1):
    h_k = simple_hash(a, val, p)
    tidemark.Process(h_k)
    s_k = tidemark.Size()
    z_k = tidemark.z
    ks.append(k)
    sizes.append(s_k)
    zs.append(z_k)
    print(f"k = {k:4d}, s*(k) = {s_k:4d} bytes, z(k) = {z_k}, val = {val}, a = {a}, p = {p}")

plt.figure(figsize=(10, 5))
plt.plot(ks, sizes, marker='o', label='s*(k): bytes used')
plt.xlabel("k (elements processed)")
plt.ylabel("Memory in bytes")
plt.title("Tidemark Overall Memory Usage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))
plt.step(ks, zs, where='post', label='z(k): max trailing zeroes')
plt.xlabel("k (elements processed)")
plt.ylabel("z(k)")
plt.title("Tidemark: Trailing Zero Count")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()