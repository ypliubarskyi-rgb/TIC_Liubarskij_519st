import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft
import os


n = 500
Fs = 1000
F_max = 13
F_filter = 20
line_width = 1
font_size = 14





time_steps = np.arange(n) / Fs


raw_noise = np.random.normal(0, 10, n)
w_initial = F_max / (Fs / 2)
sos_initial = signal.butter(3, w_initial, 'low', output='sos')
initial_signal = signal.sosfiltfilt(sos_initial, raw_noise)


discrete_signals = []
discrete_spectrums = []
recovered_signals = []
variances_e = []
snr_values = []


for Dt in [2, 4, 8, 16]:

    discrete_signal = np.zeros(n)
    for i in range(0, round(n / Dt)):
        idx = i * Dt
        if idx < n:
            discrete_signal[idx] = initial_signal[idx]

    discrete_signals += [list(discrete_signal)]


    spec = fft.fft(discrete_signal)
    spec_shifted = np.abs(fft.fftshift(spec))
    discrete_spectrums += [list(spec_shifted)]


    w_rec = F_filter / (Fs / 2)
    sos_rec = signal.butter(3, w_rec, 'low', output='sos')
    recovered = signal.sosfiltfilt(sos_rec, discrete_signal)
    recovered_signals += [list(recovered)]


    E1 = recovered - initial_signal
    var_initial = np.var(initial_signal)
    var_e = np.var(E1)

    variances_e.append(var_e)
    snr_values.append(var_initial / var_e)



def save_grid_plot(x, y_multi, title, x_label, y_label):
    fig, ax = plt.subplots(2, 2, figsize=(21 / 2.54, 14 / 2.54))
    s = 0
    steps = [2, 4, 8, 16]
    for i in range(2):
        for j in range(2):
            ax[i][j].plot(x, y_multi[s], linewidth=line_width)
            ax[i][j].set_title(f"Dt = {steps[s]}", fontsize=10)
            ax[i][j].grid(True, linestyle='--', alpha=0.5)
            s += 1

    fig.supxlabel(x_label, fontsize=font_size)
    fig.supylabel(y_label, fontsize=font_size)
    fig.suptitle(title, fontsize=font_size)
    plt.tight_layout()
    fig.savefig(f'./figures/{title}.png', dpi=600)
    plt.close(fig)



freq_axis = fft.fftshift(fft.fftfreq(n, 1 / Fs))


save_grid_plot(time_steps, discrete_signals, "Discrete_Signals", "Час (с)", "Амплітуда")
save_grid_plot(freq_axis, discrete_spectrums, "Discrete_Spectrums", "Частота (Гц)", "Амплітуда")
save_grid_plot(time_steps, recovered_signals, "Recovered_Signals", "Час (с)", "Амплітуда")


steps = [2, 4, 8, 16]


plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(steps, variances_e, 'o-', linewidth=line_width)
plt.title("Дисперсія похибки від кроку дискретизації", fontsize=font_size)
plt.xlabel("Крок дискретизації Dt", fontsize=font_size)
plt.ylabel("Дисперсія", fontsize=font_size)
plt.grid(True)
plt.savefig('./figures/Variance_Error.png', dpi=600)
plt.close()


plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(steps, snr_values, 'o-', linewidth=line_width)
plt.title("Співвідношення сигнал-шум від Dt", fontsize=font_size)
plt.xlabel("Крок дискретизації Dt", fontsize=font_size)
plt.ylabel("SNR", fontsize=font_size)
plt.grid(True)
plt.savefig('./figures/SNR_Dependency.png', dpi=600)
plt.close()

print("Обробка завершена. Перевір папку ./figures/")