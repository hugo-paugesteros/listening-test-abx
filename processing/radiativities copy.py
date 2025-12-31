import pandas as pd
from frf.dataset.synthetic import load_excerpt
import numpy as np
import matplotlib.pyplot as plt
from frf.core.signal import Signal
import pathlib
import scipy.signal

VIOLIN_NAME = ["Klimke 02", "Levaggi 02", "Stoppani 05"][1]
SR = 48000

DATA_DIR = pathlib.Path("/home/hugo/Thèse/Data")
CNSM_DIR = DATA_DIR / "CNSM/AfterOpening_CNSM"
SYNTH_INPUT_PATH = DATA_DIR / "Synthétiques/string/Sibelius.wav"
OUTPUT_DIR = pathlib.Path("../data/synth")


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


def synthesize_and_save(
    name: str,
    spectrum: np.ndarray,
    source_signal: np.ndarray,
    source_sr: int,
    output_dir: pathlib.Path,
):
    """
    Computes the Impulse Response (IR) from the spectrum, convolves it with
    the source signal, normalizes, and saves to WAV.
    """
    # plt.figure()
    # plt.plot(20 * np.log10(np.abs(spectrum)))
    # plt.xscale("log")
    # plt.xlim([200, 5000])
    # plt.show()
    h = np.fft.irfft(spectrum)
    # h = np.fft.irfft(spectrum, n=int(0.3 * SR))
    window = np.exp(-40 * np.arange(len(h) - 10000) / SR)
    h[10000:] *= window
    y = scipy.signal.fftconvolve(source_signal, h)
    y = y[: int(SR * 10)]
    y /= np.max(np.abs(y))

    y = y[np.newaxis, :]
    signal_obj = Signal(y, source_sr)

    output_path = output_dir / f"S-{VIOLIN_NAME}-E2-{name}.wav"
    output_dir.mkdir(parents=True, exist_ok=True)

    scipy.io.wavfile.write(
        output_path,
        50000,
        signal_obj.y.T,
    )
    print(f"Saved: {output_path}")


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
    violin_dir = CNSM_DIR / maker_name / VIOLIN_NAME / "csv"

    print(f"Processing Violin: {VIOLIN_NAME}")

    try:
        hv20_real_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} HV_Real.tsv").Y
        hv20_cplx_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} HV_Cplx.tsv").Y
        h1_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} H_001_trf.tsv").Y
        v1_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} V_001_trf.tsv").Y
    except FileNotFoundError as e:
        hv20_real_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} VH_Real.tsv").Y
        hv20_cplx_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} VH_Cplx.tsv").Y
        h1_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} H_001_trf.tsv").Y
        v1_frf = load_radiativity(violin_dir / f"{VIOLIN_NAME} V_001_trf.tsv").Y
        print(e)
        # return

    hv1_frf = (h1_frf + v1_frf) / 2

    string_signal = load_excerpt(str(SYNTH_INPUT_PATH), SR)
    synthesis_targets = {"HV20": hv20_cplx_frf, "HV1": hv1_frf, "H1": h1_frf}
    for name, spectrum in synthesis_targets.items():
        synthesize_and_save(
            name, spectrum, string_signal.y, string_signal.sr, OUTPUT_DIR
        )

    plot_targets = {
        "HV20": hv20_cplx_frf,
        "HV1": hv1_frf,
        "H1": h1_frf,
        "HV20 real": hv20_real_frf,
    }
    plot_responses(plot_targets)


if __name__ == "__main__":
    main()
