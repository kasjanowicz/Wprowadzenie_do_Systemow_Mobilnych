import math
import random
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Generator U(0,1) – korzystamy z wbudowanego random.random()
# ---------------------------------------------------------
def gen_u():
    return random.random()


# ---------------------------------------------------------
# Generator Poissona – Algorytm 1
# X = -1; S = 1; q = exp(-lambda)
# while S > q: S *= U; X++
# ---------------------------------------------------------
def gen_poisson(lmbda):
    X = -1
    S = 1.0
    q = math.exp(-lmbda)
    while S > q:
        S *= gen_u()
        X += 1
    return X


# ---------------------------------------------------------
# Generator normalny – metoda Boxa–Mullera (wersja biegunowa)
# Zwraca jedną liczbę N(μ, σ)
# ---------------------------------------------------------
def gen_normal(mu, sigma):
    while True:
        v1 = 2 * gen_u() - 1
        v2 = 2 * gen_u() - 1
        s = v1 * v1 + v2 * v2
        if s < 1 and s != 0:
            break
    factor = math.sqrt(-2 * math.log(s) / s)
    z = v1 * factor  # standardowe N(0,1)
    return mu + sigma * z


# ---------------------------------------------------------
# Funkcja rysująca histogram
# ---------------------------------------------------------
def show_histogram(data, title):
    plt.hist(data, bins=30, edgecolor='black', density=True)
    plt.title(title)
    plt.xlabel("Wartość")
    plt.ylabel("Gęstość / częstość")
    plt.grid(True)
    plt.show()


# ---------------------------------------------------------
# Główna część aplikacji
# ---------------------------------------------------------
def main():
    print("=== Generator rozkładów (Poisson, Normalny) ===")

    # Czy użyć ziarna?
    use_seed = input("Czy chcesz użyć ziarna? (t/n): ").lower()
    if use_seed == "t":
        seed = int(input("Podaj wartość ziarna: "))
        random.seed(seed)

    # Ile liczb generować?
    n = int(input("Ile liczb wygenerować?: "))

    # --- Poisson ---
    lmbda = float(input("Podaj λ dla rozkładu Poissona: "))
    poisson_data = [gen_poisson(lmbda) for _ in range(n)]
    show_histogram(poisson_data, f"Rozkład Poissona (λ={lmbda})")

    # --- Normalny ---
    mu = float(input("Podaj średnią μ dla rozkładu normalnego: "))
    sigma = float(input("Podaj odchylenie standardowe σ: "))
    normal_data = [gen_normal(mu, sigma) for _ in range(n)]
    show_histogram(normal_data, f"Rozkład normalny (μ={mu}, σ={sigma})")


if __name__ == "__main__":
    main()
