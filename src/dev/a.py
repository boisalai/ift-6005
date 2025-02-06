def find_prime_numbers(n):
    """Find prime numbers."""
    primes = []
    for i in range(2, n + 1):
        is_prime = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
    return primes

if __name__ == "__main__":
    primes = find_prime_numbers(1000)  # Call the function and store the result
    print(primes)  # Print the result
    print(f"Number of primes found: {len(primes)}")  # Debugging statement to check the length of the primes list