import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sp_signal
import os


os.makedirs("figures", exist_ok=True)


n = 500
Fs = 1000
F_max_pr2 = 13

t = np.arange(n) / Fs


raw_noise = np.random.normal(0, 10, n)
w_initial = F_max_pr2 / (Fs / 2)
sos_initial = sp_signal.butter(3, w_initial, 'low', output='sos')

signal_from_pr2 = sp_signal.sosfiltfilt(sos_initial, raw_noise)


fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
ax.plot(t, signal_from_pr2)
ax.set_xlabel("Час (с)")
ax.set_ylabel("Амплітуда")
ax.set_title(f"Сигнал(відфільтрований ФНЧ, Fmax = {F_max_pr2} Гц)")
fig.savefig("figures/Вихідний сигнал.png", dpi=600)
plt.close(fig)


quantized_signals = []
dispersions = []
snr_list = []


signal_power = np.mean(signal_from_pr2 ** 2)

for M in [4, 16, 64, 256]:
    bits = []


    s_min, s_max = np.min(signal_from_pr2), np.max(signal_from_pr2)
    delta = (s_max - s_min) / (M - 1)


    quantize_signal = delta * np.round((signal_from_pr2 - s_min) / delta) + s_min


    quantize_levels = np.linspace(s_min, s_max, M)
    num_bits = int(np.log2(M))
    quantize_bit = [format(b, '0' + str(num_bits) + 'b') for b in range(M)]


    quantize_table = np.c_[np.round(quantize_levels, 3), quantize_bit]
    fig, ax = plt.subplots(figsize=(14 / 2.54, max(4, M / 4) / 2.54))
    table = ax.table(cellText=quantize_table, colLabels=["Значення", "Код"], loc="center")
    table.set_fontsize(10)
    ax.axis("off")
    ax.set_title(f"Таблиця квантування M = {M}")
    fig.savefig(f"figures/Таблиця_квантування_{M}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


    error = signal_from_pr2 - quantize_signal
    dispersion = np.mean(error ** 2)
    snr = signal_power / dispersion if dispersion > 0 else 0

    dispersions.append(dispersion)
    snr_list.append(snr)
    quantized_signals.append((M, quantize_signal))




fig, axes = plt.subplots(4, 1, figsize=(21 / 2.54, 28 / 2.54), sharex=True)
for ax, (M, qs) in zip(axes, quantized_signals):
    ax.plot(t, signal_from_pr2, color='gray', alpha=0.3, label='Оригінал')
    ax.step(t, qs, linewidth=0.7, label=f'M={M}')
    ax.set_ylabel("Амплітуда")
    ax.legend(loc='upper right', fontsize=8)
axes[-1].set_xlabel("Час (с)")
fig.suptitle("Квантування відфільтрованого сигналу", fontsize=12)
fig.tight_layout()
fig.savefig("figures/Квантовані сигнали.png", dpi=600)
plt.close(fig)


M_values = [4, 16, 64, 256]
fig, ax = plt.subplots(figsize=(14 / 2.54, 10 / 2.54))
ax.plot(M_values, snr_list, marker="o", color="tab:orange")
ax.set_xlabel("Кількість рівнів M")
ax.set_ylabel("SNR (лін.)")
ax.set_xscale("log", base=2)
ax.set_xticks(M_values)
ax.set_xticklabels(M_values)
ax.grid(True, which='both', linestyle='--', alpha=0.5)
ax.set_title("Залежність SNR від M ")
fig.savefig("figures/Залежність_SNR_від_M.png", dpi=600)
plt.close(fig)

print("Інтеграція завершена. Перевірте папку /figures/")