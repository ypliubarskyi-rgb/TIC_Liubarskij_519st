import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)

n = 500
Fs = 1000
Fmax = 3

t = np.arange(n) / Fs
signal_raw = np.random.randn(n)

freqs = np.fft.rfftfreq(n, d=1/Fs)
signal_fft = np.fft.rfft(signal_raw)
signal_fft[freqs > Fmax] = 0
signal = np.fft.irfft(signal_fft, n=n)

fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
ax.plot(t, signal_raw)
ax.set_xlabel("Час (с)")
ax.set_ylabel("Амплітуда")
ax.set_title("Вихідний випадковий сигнал")
fig.savefig("figures/Вихідний сигнал.png", dpi=600)
plt.close(fig)

fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
ax.plot(t, signal)
ax.set_xlabel("Час (с)")
ax.set_ylabel("Амплітуда")
ax.set_title(f"Сигнал після обмеження частоти (Fmax = {Fmax} Гц)")
fig.savefig("figures/Відфільтрований сигнал.png", dpi=600)
plt.close(fig)

quantized_signals = []
dispersions = []
snr_list = []

signal_power = np.mean(signal ** 2)

for M in [4, 16, 64, 256]:

    bits = []

    delta = (np.max(signal) - np.min(signal)) / (M - 1)

    quantize_signal = delta * np.round(signal / delta)

    quantize_levels = np.linspace(
        np.min(quantize_signal),
        np.max(quantize_signal),
        M
    )

    num_bits = int(np.log(M) / np.log(2))
    quantize_bit = np.arange(0, M)
    quantize_bit = [format(b, '0' + str(num_bits) + 'b') for b in quantize_bit]

    quantize_table = np.c_[quantize_levels[:M], quantize_bit[:M]]

    fig, ax = plt.subplots(figsize=(14/2.54, M/2.54))
    table = ax.table(
        cellText=quantize_table,
        colLabels=["Значення сигналу", "Кодова послідовність"],
        loc="center"
    )
    table.set_fontsize(14)
    table.scale(1, 2)
    ax.axis("off")
    ax.set_title(f"Таблиця квантування для {M} рівнів", pad=12)
    fig.savefig(f"figures/Таблиця квантування для {M} рівнів.png", dpi=600, bbox_inches="tight")
    plt.close(fig)

    for signal_value in quantize_signal:
        distances = np.abs(quantize_levels[:M] - signal_value)
        index = np.argmin(distances)
        bits.append(quantize_bit[index])

    bits = [int(item) for item in list("".join(bits))]

    fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
    ax.step(np.arange(0, len(bits)), bits, linewidth=0.1)
    ax.set_xlabel("Номер біту")
    ax.set_ylabel("Значення (0 / 1)")
    ax.set_title(f"Кодова послідовність (M = {M}, {len(bits)} біт)")
    fig.savefig(f"figures/Кодова послідовність M={M}.png", dpi=600)
    plt.close(fig)

    error = signal - quantize_signal
    dispersion = np.mean(error ** 2)
    snr = signal_power / dispersion

    dispersions.append(dispersion)
    snr_list.append(snr)
    quantized_signals.append((M, quantize_signal))

fig, axes = plt.subplots(4, 1, figsize=(21/2.54, 28/2.54), sharex=True)
for ax, (M, qs) in zip(axes, quantized_signals):
    ax.plot(t, qs, linewidth=0.7)
    ax.set_ylabel("Амплітуда")
    ax.set_title(f"M = {M} рівнів")
axes[-1].set_xlabel("Час (с)")
fig.suptitle("Квантовані сигнали при різних M", fontsize=12)
fig.tight_layout()
fig.savefig("figures/Квантовані сигнали.png", dpi=600)
plt.close(fig)

M_values = [4, 16, 64, 256]

fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))
ax.plot(M_values, dispersions, marker="o")
ax.set_xlabel("Кількість рівнів квантування M")
ax.set_ylabel("Дисперсія помилки квантування")
ax.set_title("Залежність дисперсії від кількості рівнів квантування")
ax.set_xscale("log", base=2)
ax.set_xticks(M_values)
ax.set_xticklabels(M_values)
fig.savefig("figures/Залежність дисперсії від M.png", dpi=600)
plt.close(fig)

fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))
ax.plot(M_values, snr_list, marker="o", color="tab:orange")
ax.set_xlabel("Кількість рівнів квантування M")
ax.set_ylabel("Відношення сигнал/шум (лін.)")
ax.set_title("Залежність SNR від кількості рівнів квантування")
ax.set_xscale("log", base=2)
ax.set_xticks(M_values)
ax.set_xticklabels(M_values)
fig.savefig("figures/Залежність SNR від M.png", dpi=600)
plt.close(fig)