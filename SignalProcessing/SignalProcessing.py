import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft


n = 500
Fs = 1000
F_max = 13


def save_plot(x, y, xlabel, ylabel, title):
    """Функція для побудови та збереження графіків згідно з вимогами"""

    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))

    ax.plot(x, y, linewidth=1)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)


    file_path = f'./figures/{title}.png'
    fig.savefig(file_path, dpi=600)
    print(f"Графік збережено: {file_path}")
    plt.close(fig)


raw_signal = np.random.normal(0, 10, n)

time_steps = np.arange(n) / Fs

w = F_max / (Fs / 2)
sos = signal.butter(3, w, 'low', output='sos')

filtered_signal = signal.sosfiltfilt(sos, raw_signal)

save_plot(time_steps, filtered_signal, "Час (с)", "Амплітуда", "Filtered_Signal_v6")

spectrum = fft.fft(filtered_signal)

spectrum_shifted = np.abs(fft.fftshift(spectrum))

freq_axis = fft.fftfreq(n, 1 / Fs)
freq_axis_shifted = fft.fftshift(freq_axis)

save_plot(freq_axis_shifted, spectrum_shifted, "Частота (Гц)", "Амплітуда", "Signal_Spectrum_v6")

print("\nОбробка завершена успішно.")