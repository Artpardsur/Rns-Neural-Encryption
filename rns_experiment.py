#!/usr/bin/env python3

import subprocess
import numpy as np
import time
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

# ======================== ПАРАМЕТРЫ ========================
MODULI = [1009, 1013, 1019, 1021, 1031]
P_WORK = 1009 * 1013 * 1019
P_FULL = P_WORK * 1021 * 1031
P_CONTROL = 1021 * 1031

# Константы
M = [P_FULL // m for m in MODULI]

INV_M = []
for i, m in enumerate(MODULI):
    Mi = M[i]
    for inv in range(1, m):
        if (Mi * inv) % m == 1:
            INV_M.append(inv)
            break

S = []
for i, m in enumerate(MODULI):
    Mi = M[i]
    inv = INV_M[i]
    Bi = Mi * inv
    Si = (Bi - (Bi % P_WORK)) // P_WORK
    S.append(Si)

QUANT = 10000

def normalize(x, mod):
    return ((x % mod) + mod) % mod

def encrypt_via_cpp(num):
    result = subprocess.run(["./rns_final.exe", str(num)], capture_output=True, text=True)
    return [int(x) for x in result.stdout.split()]

def decrypt_to_signed(residues):
    val = 0
    for i in range(5):
        val = (val + residues[i] * M[i] * INV_M[i]) % P_FULL
    
    L = 0
    for i in range(5):
        L = (L + residues[i] * S[i]) % P_CONTROL
    
    if L != 0 and L != P_CONTROL - 1:
        val = (L * P_WORK + val) % P_FULL
    
    if val > P_FULL // 2:
        val = val - P_FULL
    
    val = val % P_WORK
    if val > P_WORK // 2:
        val = val - P_WORK
    
    return val

def experiment_paillier(model, X_sample):
    try:
        from phe import paillier
    except ImportError:
        return None
    
    w = model.coefs_[0][:, 0]
    b = model.intercepts_[0][0]
    x = X_sample.flatten()
    
    print("    - Генерация ключей Paillier...")
    start = time.perf_counter()
    pub, priv = paillier.generate_paillier_keypair(n_length=2048)
    key_time = time.perf_counter() - start
    
    print("    - Шифрование весов...")
    start = time.perf_counter()
    enc_w = [pub.encrypt(float(w_i)) for w_i in w]
    enc_time = time.perf_counter() - start
    
    print("    - Вычисление...")
    start = time.perf_counter()
    result = pub.encrypt(0)
    for w_enc, x_i in zip(enc_w, x):
        result = result + (w_enc * x_i)
    result = result + b
    inf_time = time.perf_counter() - start
    
    print("    - Расшифровка...")
    start = time.perf_counter()
    decrypted = priv.decrypt(result)
    dec_time = time.perf_counter() - start
    
    normal = np.dot(w, x) + b
    error = abs(normal - decrypted) / (abs(normal) + 1e-8)
    
    return {
        'encrypt_time': enc_time,
        'inference_time': inf_time,
        'decrypt_time': dec_time,
        'keygen_time': key_time,
        'error': error,
        'normal': normal,
        'decrypted': decrypted
    }

def main():
    print("=" * 80)
    print("RNS ШИФРОВАНИЕ НЕЙРОСЕТИ — СРАВНЕНИЕ С PAILLIER")
    print("=" * 80)
    
    # Данные и модель
    data = load_breast_cancer()
    X, y = data.data, data.target
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = MLPClassifier(hidden_layer_sizes=(10,), max_iter=500, random_state=42)
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"\nТочность модели: {acc:.4f}")
    
    # Берём один тестовый пример
    X_sample = X_test[0]
    y_sample = y_test[0]
    print(f"Тестовый пример, правильный ответ: {y_sample}")
    
    w = model.coefs_[0][:, 0]
    b = model.intercepts_[0][0]
    x = X_sample.flatten()
    
    # Обычный результат
    normal_float = np.dot(w, x) + b
    
    # Квантованные значения
    w_int = [int(round(v * QUANT)) for v in w]
    x_int = [int(round(v * QUANT)) for v in x]
    b_int = int(round(b * QUANT))
    
    # ПРАВИЛЬНЫЙ int: сумма произведений
    normal_int = sum(w_int[i] * x_int[i] for i in range(len(w))) + b_int
    
    print(f"\nОбычный результат (float): {normal_float:.10f}")
    print(f"Обычный результат (int):   {normal_int}")
    
    # ======================== ЭКСПЕРИМЕНТ С RNS ========================
    print("\n--- Эксперимент 1: C++ RNS ---")
    
    # Нормализация
    w_norm = [normalize(v, P_WORK) for v in w_int]
    x_norm = [normalize(v, P_WORK) for v in x_int]
    b_norm = normalize(b_int, P_WORK)
    
    # Шифрование через C++
    start = time.perf_counter()
    enc_w = [encrypt_via_cpp(v) for v in w_norm]
    enc_time = time.perf_counter() - start
    print(f"  Время шифрования: {enc_time:.6f} с")
    print(f"  Пример шифрования: {enc_w[0]}")
    
    # Вычисление в зашифрованном виде
    start = time.perf_counter()
    enc_result = [0] * 5
    for mod_idx, mod in enumerate(MODULI):
        total = 0
        for i in range(len(w)):
            total = (total + enc_w[i][mod_idx] * (x_norm[i] % mod)) % mod
        total = (total + (b_norm % mod)) % mod
        enc_result[mod_idx] = total
    inf_time = time.perf_counter() - start
    print(f"  Время inference: {inf_time:.6f} с")
    print(f"  Остатки результата: {enc_result}")
    
    # Расшифровка
    start = time.perf_counter()
    dec_signed = decrypt_to_signed(enc_result)
    dec_time = time.perf_counter() - start
    print(f"  Время расшифровки: {dec_time:.6f} с")
    
    dec_float = dec_signed / QUANT
    
    print(f"  Расшифрованный (int): {dec_signed}")
    print(f"  Расшифрованный (float): {dec_float:.10f}")
    
    # ПРАВИЛЬНОЕ СРАВНЕНИЕ
    if dec_signed == normal_int:
        print("  ✅ ТОЧНОСТЬ: 100% (int совпадает)")
        error_rns = 0
    else:
        diff = abs(dec_signed - normal_int)
        error_rns = diff / abs(normal_int) * 100 if normal_int != 0 else 100
        print(f"  ⚠️ ТОЧНОСТЬ: расхождение {diff} ({error_rns:.6f}%)")
    
    # ======================== ЭКСПЕРИМЕНТ С PAILLIER ========================
    print("\n--- Эксперимент 2: Paillier ---")
    paillier_results = experiment_paillier(model, X_sample)
    
    if paillier_results is None:
        print("  Paillier не установлен. Установите: pip install phe")
        return
    
    # ======================== СВОДНАЯ ТАБЛИЦА ========================
    print("\n" + "=" * 80)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 80)
    print(f"{'Метрика':<35} {'RNS (C++)':<20} {'Paillier':<15}")
    print("-" * 70)
    print(f"{'Время шифрования (с)':<35} {enc_time:<20.6f} {paillier_results['encrypt_time']:<15.6f}")
    print(f"{'Время inference (с)':<35} {inf_time:<20.6f} {paillier_results['inference_time']:<15.6f}")
    print(f"{'Время расшифровки (с)':<35} {dec_time:<20.6f} {paillier_results['decrypt_time']:<15.6f}")
    print(f"{'Относительная ошибка (%)':<35} {error_rns:<20.6f} {paillier_results['error'] * 100:<15.6f}")
    print(f"{'Нормальный результат (int)':<35} {normal_int:<20} {'N/A':<15}")
    print(f"{'Расшифрованный (int)':<35} {dec_signed:<20} {'N/A':<15}")
    print("=" * 80)
    
    # ======================== ВЫВОДЫ ========================
    print("\n" + "=" * 80)
    print("ВЫВОДЫ")
    print("=" * 80)
    speedup_enc = paillier_results['encrypt_time'] / enc_time if enc_time > 0 else 0
    speedup_inf = paillier_results['inference_time'] / inf_time if inf_time > 0 else 0
    print(f"1. ⚡ СКОРОСТЬ ШИФРОВАНИЯ: C++ RNS в {speedup_enc:.0f} раз БЫСТРЕЕ Paillier")
    print(f"2. ⚡ СКОРОСТЬ INFERENCE: C++ RNS в {speedup_inf:.0f} раз БЫСТРЕЕ Paillier")
    print(f"3. 🎯 ТОЧНОСТЬ: Ошибка RNS = {error_rns:.6f}%")
    if error_rns == 0:
        print("   ✅ ИДЕАЛЬНО! 100% точность")
    elif error_rns < 0.1:
        print("   ✅ ОТЛИЧНО! Ошибка менее 0.1%")
    elif error_rns < 1:
        print("   ✅ ХОРОШО! Ошибка менее 1%")
    else:
        print(f"   ⚠️ Ошибка {error_rns:.2f}%")
    print("=" * 80)

if __name__ == "__main__":
    main()