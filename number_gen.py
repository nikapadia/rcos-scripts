import random

NUM_UNIQUE = 150

unique_numbers = set()
while len(unique_numbers) < NUM_UNIQUE:
    unique_numbers.add(random.randint(1000, 9999))
print(unique_numbers)

