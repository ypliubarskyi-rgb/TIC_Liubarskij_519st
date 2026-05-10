import collections
import math
import os
import ast


def encode_rle(sequence):
    if not sequence:
        return ""
    result = ""
    i = 0
    while i < len(sequence):
        count = 1
        while i + 1 < len(sequence) and sequence[i] == sequence[i + 1]:
            count += 1
            i += 1

        result += str(count) + sequence[i]
        i += 1
    return result


def encode_lzw(sequence):

    dictionary = {s: i for i, s in enumerate(sorted(list(set(sequence))))}
    dict_size = len(dictionary)
    w = ""
    result = []
    for c in sequence:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
    if w:
        result.append(dictionary[w])
    return result



if not os.path.exists('LosslessCompression/LosslessCompression/sequence.txt'):
    print("Помилка: Файл sequence.txt не знайдено!")
    exit()

with open("LosslessCompression/LosslessCompression/sequence.txt", "r", encoding="utf-8") as file:

    content = file.read().splitlines()

    original_sequences = [s.strip() for s in content if s.strip()]


with open("LosslessCompression/results_rle_lzw.txt", "w", encoding="utf-8") as f_res:
    f_res.write("Результати практичної роботи №6\n")
    f_res.write(f"Виконав: Любарський Є.П., група 519\n")
    f_res.write("=" * 50 + "\n\n")

    for idx, seq in enumerate(original_sequences, 1):
        N_seq = len(seq)
        counts = collections.Counter(seq)
        prob = {s: c / N_seq for s, c in counts.items()}
        entropy = -sum(p * math.log2(p) for p in prob.values())


        initial_bits = N_seq * 16


        rle_encoded = encode_rle(seq)

        rle_bits = len(rle_encoded) * 16
        rle_ratio = initial_bits / rle_bits if rle_bits > 0 else 0


        lzw_encoded = encode_lzw(seq)

        lzw_bits = len(lzw_encoded) * 16
        lzw_ratio = initial_bits / lzw_bits if lzw_bits > 0 else 0

        # Запис у файл
        f_res.write(f"Послідовність №{idx}:\n{seq}\n")
        f_res.write(f"Ентропія: {entropy:.4f}\n")
        f_res.write(f"Початковий розмір: {initial_bits} біт\n")
        f_res.write(f"RLE результат: {rle_encoded} (Розмір: {rle_bits} біт, КС: {rle_ratio:.2f})\n")
        f_res.write(f"LZW кількість кодів: {len(lzw_encoded)} (Розмір: {lzw_bits} біт, КС: {lzw_ratio:.2f})\n")
        f_res.write("-" * 30 + "\n")

print("Стиснення завершено. Результати у файлі results_rle_lzw.txt")