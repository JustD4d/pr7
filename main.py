import random
import os
import math


# ====================== МАТЕМАТИЧЕСКИЕ ФУНКЦИИ ======================
def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Расширенный алгоритм Евклида."""
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def mod_inverse(e: int, phi: int) -> int:
    """Нахождение обратного элемента по модулю."""
    g, x, y = egcd(e, phi)
    if g != 1:
        raise Exception("Обратный элемент не существует")
    return x % phi


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Быстрое возведение в степень по модулю."""
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result


# ====================== ТЕСТЫ НА ПРОСТОТУ ======================
def is_prime_fermat(n: int, iterations: int = 50) -> bool:
    """Тест Ферма на простоту."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    for _ in range(iterations):
        a = random.randint(2, n - 2)
        if mod_pow(a, n - 1, n) != 1:
            return False
    return True


def generate_prime(bits: int) -> int:
    """Генерация простого числа."""
    while True:
        p = random.getrandbits(bits)
        p |= (1 << (bits - 1)) | 1
        if is_prime_fermat(p, iterations=40 if bits > 40 else 10):
            return p


# ====================== RSA ======================
def generate_keypair(bits: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Генерация ключей RSA."""
    if bits < 16:
        bits = 16
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = mod_inverse(e, phi)

    return (e, n), (d, n)


# ====================== ФЕРМАТ ФАКТОРИЗАЦИЯ (АТАКА) ======================
def fermat_factorization(n: int, max_steps: int = 10000):
    """Атака: Факторизация методом Ферма (для близких p и q)."""
    print(f"\nВыполняется атака Ферма на n = {n} ...")
    a = int(math.isqrt(n)) + 1
    for i in range(max_steps):
        b2 = a*a - n
        b = int(math.isqrt(b2))
        if b*b == b2:
            p = a - b
            q = a + b
            print(f"Факторизация успешна за {i} шагов!")
            print(f"p = {p}")
            print(f"q = {q}")
            return p, q
        a += 1
    print("Не удалось факторизовать за заданное число шагов.")
    return None, None


# ====================== РАБОТА С ФАЙЛАМИ ======================
def save_key(filename: str, key: tuple[int, int]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{key[0]},{key[1]}")


def load_key_interactive(default_filename: str):
    prompt = f"Введите имя файла ключа (Enter для '{default_filename}'): "
    user_input = input(prompt).strip()
    filename = user_input if user_input else default_filename

    if not os.path.exists(filename):
        print(f"Ошибка: Файл '{filename}' не найден.")
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read().strip().split(",")
            return int(data[0]), int(data[1])
    except Exception:
        print("Ошибка: Некорректный формат файла.")
        return None


def rsa_encrypt_file(public_key, input_file, output_file):
    e, n = public_key
    if not os.path.exists(input_file):
        print(f"Создаю пример {input_file}...")
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("Тестовое сообщение для лабораторной работы 7.")

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    cipher_blocks = [mod_pow(ord(char), e, n) for char in text]

    with open(output_file, "w") as f:
        f.write(",".join(map(str, cipher_blocks)))

    print(f"\nФайл успешно зашифрован → {output_file} ({len(text)} символов)")


def rsa_decrypt_file(private_key, input_file, output_file):
    d, n = private_key
    if not os.path.exists(input_file):
        print(f"Ошибка: {input_file} не найден.")
        return

    with open(input_file, "r") as f:
        cipher_blocks = list(map(int, f.read().strip().split(",")))

    plain_text = "".join(chr(mod_pow(c, d, n)) for c in cipher_blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(plain_text)

    print(f"\nФайл успешно расшифрован → {output_file}")
    print("=" * 60)
    print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ:")
    print("-" * 60)
    print(plain_text)
    print("-" * 60)


# ====================== МЕНЮ ======================
def main():
    while True:
        print("\n" + "=" * 60)
        print("          RSA — ПРАКТИЧЕСКАЯ РАБОТА 7")
        print("=" * 60)
        print("1. Сгенерировать ключевую пару")
        print("2. Зашифровать файл")
        print("3. Расшифровать файл")
        print("4. Атака Ферма (факторизация)")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == '1':
            bits = int(input("Размер ключа в битах (16–2048, рекомендуется 1024): "))
            pub, priv = generate_keypair(bits)
            save_key("public.key", pub)
            save_key("private.key", priv)
            print("\nКлючи успешно сгенерированы!")
            print(f"Публичный:  public.key  (e={pub[0]}, n={pub[1]})")
            print(f"Приватный:  private.key (d=..., n={priv[1]})")

        elif choice == '2':
            key = load_key_interactive("public.key")
            if key:
                infile = input("Файл для шифрования (Enter → input.txt): ").strip() or "input.txt"
                rsa_encrypt_file(key, infile, "encrypted.txt")

        elif choice == '3':
            key = load_key_interactive("private.key")
            if key:
                infile = input("Файл для расшифрования (Enter → encrypted.txt): ").strip() or "encrypted.txt"
                rsa_decrypt_file(key, infile, "decrypted.txt")

        elif choice == '4':
            try:
                n = int(input("Введите модуль n для атаки: "))
                fermat_factorization(n)
            except ValueError:
                print("Ошибка: введите корректное число.")

        elif choice == '0':
            print("До свидания!")
            break


if __name__ == "__main__":
    main()
