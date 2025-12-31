import pandas as pd
from frf.dataset.synthetic import load_excerpt
import numpy as np
import matplotlib.pyplot as plt
from frf.core.signal import Signal
import pathlib
import scipy.signal
import librosa

VIOLIN_NAME = ["Klimke 02", "Levaggi 02", "Stoppani 05"][2]
SR = 48000

DATA_DIR = pathlib.Path("/home/hugo/Thèse/Data")
CNSM_DIR = DATA_DIR / "CNSM/AfterOpening_CNSM"


def load_radiativity(filename):
    try:
        frf = pd.read_csv(filename, sep="\t", decimal=",", dtype=np.float32)
    except (ValueError, pd.errors.ParserError):
        frf = pd.read_csv(filename, sep="\t", dtype=np.float32)

    if "real" in frf.columns:
        re = frf.iloc[:, 1]
        im = frf.iloc[:, 2]
        Y = re.values + 1j * im.values
    else:
        Y = frf.iloc[:, 1].values
    sr = (Y.shape[0] - 1) * 2

    return Signal.from_spectrum(Y, sr)


def plot_responses(data_dict: dict):
    """
    Plots the magnitude of the frequency responses.
    """
    n_bins = SR // 2 + 1
    nyquist = SR // 2
    f = np.arange(n_bins) / n_bins * nyquist

    fig, ax = plt.subplots(figsize=(10, 6))

    for label, spectrum in data_dict.items():
        magnitude_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
        offset = magnitude_db[(f > 200) & (f < 400)].max()
        magnitude_db -= offset
        ax.plot(f, magnitude_db, label=label)

    ax.set_xlim([200, 5000])
    ax.set_xscale("log")
    ax.set_xticks([200, 500, 1000, 5000])
    ax.set_xticklabels(["200", "500", "1k", "5k"])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title(f"Frequency Response: {VIOLIN_NAME}")
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.5)
    plt.show()


def main():
    maker_name = VIOLIN_NAME[:-3]
    csv_dir = CNSM_DIR / maker_name / VIOLIN_NAME / "csv"
    wav_dir = CNSM_DIR / maker_name / VIOLIN_NAME / "Raw"

    print(f"Processing Violin: {VIOLIN_NAME}")
    h1_frf = load_radiativity(csv_dir / f"{VIOLIN_NAME} H_001_trf.tsv").Y
    X = np.zeros((10, SR // 2 + 1), dtype=np.complex64)
    Y = np.zeros((10, SR // 2 + 1), dtype=np.complex64)
    files = wav_dir.glob(f"{VIOLIN_NAME} H_001_*.wav")
    for i, file in enumerate(files):
        y, sr = librosa.load(file, sr=None, mono=False)
        x = y[1]
        y = y[0]
        X[i] = np.fft.rfft(x, SR)
        Y[i] = np.fft.rfft(y, SR)
    # Pxy = (Y * np.conj(X)).mean(axis=0)
    # Pxx = (X * np.conj(X)).mean(axis=0)
    # h1_frf_wav = Pxy / (Pxx)
    h1_frf_wav = (Y / X).mean(axis=0)
    print(h1_frf.shape)
    print(h1_frf_wav.shape)

    plot_responses(
        {
            "h1_frf": h1_frf,
            "h1_frf_wav": h1_frf_wav,
        }
    )


if __name__ == "__main__":
    main()
