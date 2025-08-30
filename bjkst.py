import matplotlib.pyplot as plt
import sys
import random
import math

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
    raise ValueError("No prime found")

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

def get_ind_size(ind_obj, ind_seen=None):
    ind_size = sys.getsizeof(ind_obj)
    if ind_seen is None:
        ind_seen = set()
    ind_obj_id = id(ind_obj)
    if ind_obj_id in ind_seen:
        return 0
    ind_seen.add(ind_obj_id)
    if isinstance(ind_obj, dict):
        size += sum(get_size(k, ind_seen) + get_size(v, ind_seen) for k, v in ind_obj.items())
    #elif hasattr(ind_obj, '__dict__'):
    #    ind_size += get_size(ind_obj.__dict__, ind_seen)
    elif hasattr(ind_obj, '__iter__') and not isinstance(ind_obj, (str, bytes, bytearray)):
        ind_size += sum(get_size(i, ind_seen) for i in ind_obj)
    return ind_size

def hashfn(a, b, k, p):
    return (b+ a * k) % p

class BJKST:
    def __init__(self, a_h, a_g, p, k, T, a_add):
        self.a_h = a_h
        self.a_g = a_g
        self.p = p
        self.k = k
        self.T = T
        self.a_add = a_add
        self.z = 0
        self.B = set()

    def h(self, x):
        return hashfn(self.a_h,self.a_add, x, self.p)

    def g(self, x):
        return hashfn(self.a_h,self.a_add, x, self.p) % self.k

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
    
    def indSize(self):
        return get_ind_size(self)
    
# === Read Stream from file ===
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

epsilon = 0.2
n = 10000 
p = get_random_prime_between(10001, 20000)
a_h = random.randint(1, p - 1)
a_add = random.randint(1, p - 1)
a_g = get_random_prime_between(1, p - 1)
k_range = int((math.log2(n) ** 2) / (epsilon ** 4)) + 1
T = int(1 / (epsilon ** 2)) + 1
budget_s = 794000

# fixing hashes
fixed_a_h = a_h
fixed_a_g = a_g
fixed_a_add = a_add
fixed_p = p

bjkst = BJKST(fixed_a_h, fixed_a_g,fixed_a_add, fixed_p, k_range, T)
ks, s_stars, zs = [], [], []
individual_s_stars = []
max_s_star= 0
total_reqd_s = 0
for idx, x in enumerate(stream_values, start=1):
    # Process stream element
    bjkst.Process(x)
    s_k = bjkst.Size()
    if s_k > budget_s:
        #raise MemoryError(f"Memory budget exceeded at k = {idx}, s*(k) = {s_k} > {budget_s} bytes.")
        print(f"Memory budget exceeded at k = {idx}, s*(k) = {s_k} > {budget_s} bytes.")
        raise MemoryError(f"Memory budget exceeded at k = {idx}, s*(k) = {s_k} > {budget_s} bytes.")
        #sys.exit(1)
    z_k = bjkst.z
    ks.append(idx + 1)
    s_stars.append(s_k)
    zs.append(z_k)

    # Individual s*(x)
    bjkst_temp = BJKST(fixed_a_h, fixed_a_g,fixed_a_add, fixed_p, k_range, T)
    bjkst_temp.Process(x)

    single_size = bjkst_temp.indSize()
    individual_s_stars.append(single_size)
    if single_size > max_s_star:
        max_s_star = single_size
    print(f"x = {idx + 1:3d}, s*(x) = {single_size:4d} bytes, z(x) = {bjkst_temp.z}, a_h = {fixed_a_h}, a_g = {fixed_a_g}, p = {fixed_p}")
print(max_s_star)
print("Total size required to run this: ",s_k, " budget allocated is ", budget_s)
# Overall memory used by python
plt.figure(figsize=(10, 5))
plt.plot(ks, s_stars, marker='o', label='s*(k): bytes used')
plt.xlabel("k (elements processed)")
plt.ylabel("Memory in bytes")
plt.title("BJKST overall memory used by python")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Trailing zeroes
plt.figure(figsize=(10, 4))
plt.step(ks, zs, where='post', label='z(k): max trailing zeroes')
plt.xlabel("k (elements processed)")
plt.ylabel("z(k)")
plt.title("BJKST trailing zero counts")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Individual size plot
plt.figure(figsize=(10, 5))
plt.plot(range(1, n + 1), individual_s_stars, marker='o', label='s*(x): memory for single element')
plt.xlabel("x (element inserted first)")
plt.ylabel("Memory in bytes")
plt.title("Minimum Memory s*(x) Required to Process Single Element in BJKST")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()