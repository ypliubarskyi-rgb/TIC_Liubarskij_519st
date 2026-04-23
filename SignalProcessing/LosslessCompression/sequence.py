import random
import string
import collections
import math
import os
import matplotlib.pyplot as plt

if not os.path.exists('LosslessCompression'):
    os.makedirs('LosslessCompression')

student_surname = "Любарський"
group_student = "519"
number_student = 3
N_SEQ = 100

original_sequences = []

s1_list = ['1'] * number_student + ['0'] * (N_SEQ - number_student)
random.shuffle(s1_list)
original_sequences.append("".join(s1_list))

s2_list = list(student_surname) + ['0'] * (N_SEQ - len(student_surname))
original_sequences.append("".join(s2_list))

s3_list = list(student_surname) + ['0'] * (N_SEQ - len(student_surname))
random.shuffle(s3_list)
original_sequences.append("".join(s3_list))

letters_4 = list(student_surname) + list(group_student)
repeats = N_SEQ // len(letters_4)
rem = N_SEQ % len(letters_4)
original_sequences.append("".join(letters_4 * repeats + letters_4[:rem]))

chars_5 = list(set(student_surname[:2] + group_student))

s5_list = chars_5 * 20
random.shuffle(s5_list)
original_sequences.append("".join(s5_list))

letters_6 = list(student_surname[:2])
digits_6 = list(group_student)
n_let = int(0.7 * N_SEQ)
n_dig = N_SEQ - n_let
s6_list = [random.choice(letters_6) for _ in range(n_let)] + [random.choice(digits_6) for _ in range(n_dig)]
random.shuffle(s6_list)
original_sequences.append("".join(s6_list))

chars_7 = string.ascii_lowercase + string.digits
original_sequences.append("".join(random.choice(chars_7) for _ in range(N_SEQ)))

original_sequences.append("1" * N_SEQ)

results_for_table = []
with open("LosslessCompression/sequence.txt", "w", encoding="utf-8") as f_seq:
    f_seq.write("\n".join(original_sequences))

with open("LosslessCompression/results_sequence.txt", "a", encoding="utf-8") as f_res:
    for i, seq in enumerate(original_sequences, 1):
        alphabet_size = len(set(seq))
        byte_size = len(seq)
        counts = collections.Counter(seq)
        prob = {s: c / N_SEQ for s, c in counts.items()}
        entropy = -sum(p * math.log2(p) for p in prob.values())
        if alphabet_size > 1:
            excess = 1 - (entropy / math.log2(alphabet_size))
        else:
            excess = 1.0
        mean_p = sum(prob.values()) / len(prob)
        is_equal = all(abs(p - mean_p) < 0.05 * mean_p for p in prob.values())
        uniformity = "рівна" if is_equal else "нерівна"
        prob_str = ', '.join([f"{s}={p:.4f}" for s, p in prob.items()])
        f_res.write(f"Послідовність №{i}:\n{seq}\n")
        f_res.write(f"Розмір алфавіту: {alphabet_size}, Розмір: {byte_size} байт\n")
        f_res.write(f"Ймовірності: {prob_str}\n")
        f_res.write(f"Ентропія: {entropy:.4f}, Надмірність: {excess:.4f}, Тип: {uniformity}\n\n")
        results_for_table.append([alphabet_size, round(entropy, 2), round(excess, 2), uniformity])

fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
headers = ['Розмір алфавіту', 'Ентропія', 'Надмірність', 'Ймовірність']
rows = [f'Послідовність {i}' for i in range(1, 9)]
table = ax.table(cellText=results_for_table, colLabels=headers, rowLabels=rows, loc='center', cellLoc='center')
table.set_fontsize(12)
table.scale(1, 2)
plt.title("Характеристики сформованих послідовностей")
fig.savefig('LosslessCompression/Характеристики.png', dpi=300, bbox_inches='tight')

