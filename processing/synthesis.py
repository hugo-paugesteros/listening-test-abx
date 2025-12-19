import pandas as pd
import scipy.signal
from frf.core.signal import Signal
from frf.dataset.synthetic import load_radiativity, load_excerpt
import cut
import numpy as np

radiativities_md = pd.read_pickle(
    "/home/hugo/Thèse/frf/data/processed/radiativities.pkl"
)
string_md = pd.read_pickle("/home/hugo/Thèse/frf/data/processed/string_signals.pkl")

radiativities_md = radiativities_md[
    radiativities_md.violin.isin(["Klimke", "Levaggi", "Stoppani"])
]
radiativities_md.replace(
    {"Klimke": "VA", "Levaggi": "VB", "Stoppani": "VC"}, inplace=True
)
string_md = string_md[string_md.excerpt == "sibelius"]

for radiativity_row in radiativities_md.itertuples():
    radiativity_signal = load_radiativity(radiativity_row.filename)

    for string_row in string_md.itertuples(index=False):
        string_signal = load_excerpt(string_row.filename, 48000)
        y = scipy.signal.fftconvolve(string_signal.y, radiativity_signal.y)
        y = y[np.newaxis, :]
        signal = Signal(y, string_signal.sr)
        scipy.io.wavfile.write(
            f"data/raw/S-{radiativity_row.violin}-E2-{radiativity_row.Index}.wav",
            50000,
            signal.y.T,
        )

        audio = signal.y[0, : int(signal.sr * 8.5)]
        scipy.io.wavfile.write(
            f"data/auto-cut/S-{radiativity_row.violin}-E2-{radiativity_row.Index}.wav",
            50000,
            audio.T,
        )
