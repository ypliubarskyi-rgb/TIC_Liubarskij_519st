import collections
import math
import os
import matplotlib.pyplot as plt


def encode_rle(sequence):
    if not sequence: return ""
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
    if w: result.append(dictionary[w])
    return result


def encode_ac(sequence):
    N_seq = len(sequence)
    counts = collections.Counter(sequence)
    alphabet = sorted(counts.keys())
    prob = [counts[char] / N_seq for char in alphabet]
    low, high = 0.0, 1.0
    for char in sequence:
        idx = alphabet.index(char)
        p_low = sum(prob[:idx])
        p_high = p_low + prob[idx]
        diff = high - low
        high = low + diff * p_high
        low = low + diff * p_low
    point = (low + high) / 2
    return [point, len(alphabet), alphabet, prob], point


def encode_ch(uniq_chars, probabilitys, sequence):
    alphabet = list(uniq_chars)
    if len(alphabet) <= 1:
        code_val = "0" * len(sequence)
        return [code_val, [[alphabet[0], "0"]]], code_val

    final = [[char, probabilitys[char]] for char in alphabet]
    final.sort(key=lambda x: x[1])
    tree = []
    temp_final = [item[:] for item in final]
    while len(temp_final) > 1:
        left = temp_final.pop(0)
        right = temp_final.pop(0)
        tot = left[1] + right[1]
        tree.append([left[0], right[0]])
        temp_final.append([left[0] + right[0], tot])
        temp_final.sort(key=lambda x: x[1])

    tree.reverse()
    alphabet.sort()
    symbol_code = []
    for i in range(len(alphabet)):
        code = ""
        for j in range(len(tree)):
            if alphabet[i] in tree[j][0]:
                code += '0'
                if alphabet[i] == tree[j][0]: break
            elif alphabet[i] in tree[j][1]:
                code += '1'
                if alphabet[i] == tree[j][1]: break
        symbol_code.append([alphabet[i], code])

    code_dict = {item[0]: item[1] for item in symbol_code}
    encode_str = "".join([code_dict[c] for c in sequence])
    return [encode_str, symbol_code], encode_str



base_dir = os.path.dirname(os.path.abspath(__file__))

possible_paths = [
    os.path.join(base_dir, 'LosslessCompression', 'sequence.txt'),
    os.path.join(base_dir, 'sequence.txt')
]

input_path = None
for path in possible_paths:
    if os.path.exists(path):
        input_path = path
        break



with open(input_path, "r", encoding="utf-8") as file:
    original_sequences = [s.strip() for s in file.read().splitlines() if s.strip()]

table_results = []
output_dir = os.path.dirname(input_path)
output_txt = os.path.join(output_dir, "results_AC_CH.txt")

with open(output_txt, "w", encoding="utf-8") as f:
    f.write("Результати ПР №6\nВиконав: Любарський Є.П., група 519ст\n\n")

    for idx, seq in enumerate(original_sequences, 1):
        N = len(seq)
        counts = collections.Counter(seq)
        prob_dict = {s: c / N for s, c in counts.items()}


        entropy = abs(round(-sum(p * math.log2(p) for p in prob_dict.values() if p > 0), 2))


        _, ac_point = encode_ac(seq)
        bps_ac = 32 / N


        _, ch_str = encode_ch(counts.keys(), prob_dict, seq)
        bps_ch = len(ch_str) / N if N > 0 else 0

        table_results.append([entropy, round(bps_ac, 2), round(bps_ch, 2)])

        f.write(f"Послідовність №{idx}: {seq}\n")
        f.write(f"Ентропія: {entropy}\n")
        f.write(f"AC Point: {ac_point}, BPS AC: {bps_ac:.2f}\n")
        f.write(f"CH Code: {ch_str}, BPS CH: {bps_ch:.2f}\n")
        f.write("-" * 50 + "\n")


fig, ax = plt.subplots(figsize=(12, len(original_sequences) * 0.6))
ax.axis('off')
headers = ['Ентропія', 'bps AC', 'bps CH']
rows = [f'Послідовність {i + 1}' for i in range(len(original_sequences))]

table = ax.table(cellText=table_results,
                 colLabels=headers,
                 rowLabels=rows,
                 loc='center',
                 cellLoc='center')

table.set_fontsize(12)
table.scale(1, 2)
plt.title("Результати стиснення методами AC та CH", pad=20)


fig.savefig(os.path.join(output_dir, "Результати_стиснення_AC_CH.png"), bbox_inches='tight')
print(f"Роботу завершено. Файли збережено в: {output_dir}")