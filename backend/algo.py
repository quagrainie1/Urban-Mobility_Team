class HashTable:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for _ in range (self.size)]
        self.count = 0

    def get_index(self, key):
        return (key[0] * 31 + key[1]) % self.size

    def add(self, key):
        bucket = self.buckets[self.get_index(key)]
        for item in bucket:
            if item[0] == key:
                item[1] += 1
                return
        bucket.append([key, 1])
        self.count += 1
        if self.count > self.size * 0.75:
            self.resize()

    def resize(self):
        old = self.buckets
        self.size = self.size * 2
        self.buckets = [[] for _ in range(self.size)]
        for bucket in old:
            for item in bucket:
                self.buckets[self.get_index(item[0])].append(item)


class MinHeap:
    def __init__(self):
        self.items = [] #every item is used to represent [count, key]

    def push(self, item):
        self.items.append(item)
        i = len(self.items) - 1
        while i > 0:
            parent = (i-1) // 2
            if self.items[i][0] < self.items[parent][0]:
                self.items[i], self.items[parent] = self.items[parent], self.items[i]
                i = parent
            else:
                break

    def sift_down(self, i):
        n = len(self.items)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i
            if left < n and self.items[left][0] < self.items[smallest][0]:
                smallest = left
            if right < n and self.items[right][0] < self.items[smallest][0]:
                smallest = right
            if smallest == i:
                break
            self.items[i], self.items[smallest] = self.items[smallest], self.items[i]
            i = smallest

    def pop(self):
        smallest = self.items[0]
        last = self.items.pop()
        if len(self.items) > 0:
            self.items[0] = last
            self.sift_down(0)
        return smallest


def top_k_routes(pairs, k):
    # this is used to count trips for every (pickup, dropoff) pair
    table = HashTable()
    for pu, dro in pairs:
        table.add((pu, dro))

    # this helps to keep only k biggest counts in a min-heap
    heap = MinHeap()
    for bucket in table.buckets:
        for key, count in bucket:
            if len(heap.items) < k:
                heap.push([count, key])
            elif count > heap.items[0][0]:
                heap.items[0] = [count, key]
                heap.sift_down(0)

    # pop gives the smallest first, so we insert it at the front
    result = []
    while len(heap.items) > 0:
        count, key = heap.pop()
        result.insert(0, (key, count))
    return result