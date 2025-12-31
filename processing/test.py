import csv
import pandas as pd
import scipy.io
import librosa
import os
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import cut

SR = 48000

END = int(6.90 * SR / 512)
MARGIN = int(0.1 * SR / 512)

stimulis = set()
with open("test.csv") as csvfile:
    reader = csv.reader(
        csvfile,
        delimiter="\t",
    )

    for row in reader:
        for stimuli in row:
            P, V, E = stimuli.split("-")
            if V == "VX1":
                stimulis.add(f"{P}-VA-{E}")
                stimulis.add(f"{P}-VB-{E}")
            elif V == "VX2":
                stimulis.add(f"{P}-VA-{E}")
                stimulis.add(f"{P}-VC-{E}")
            else:
                stimulis.add(stimuli)

if not os.path.exists("../data/raw"):
    os.makedirs("../data/raw")
if not os.path.exists("../data/auto-cut"):
    os.makedirs("../data/auto-cut")
dataset = pd.read_pickle(
    "/home/hugo/Thèse/identification/data/processed/dataset_cnsm.pkl"
)
dataset.rename(columns={"extract": "excerpt"}, inplace=True)
dataset.drop_duplicates(["start", "end", "file"], inplace=True)


PLAYERS = {
    "P1": "SMD",
    "P2": "Norimi",
    "P3": "Renato",
    "P4": "Clara",
}
VIOLINS = {
    "VA": ["A"],
    "VB": ["B"],
    "VC": ["C"],
}
EXCERPTS = {
    "E1": ("glazounov", 1),
    "E1'": ("glazounov", 2),
    "E1.3": ("glazounov", 3),
    "E2": ("sibelius", 3),
    "E3": ("tchai", 1),
}
for stimuli in sorted(stimulis):
    print(stimuli)
    P, V, E = stimuli.split("-")

    player = PLAYERS[P]
    violin = VIOLINS.get(V, ["A", "B", "C"])
    excerpt, session = EXCERPTS[E]

    rows = dataset[
        (dataset.player == player)
        & (dataset.violin.isin(violin))
        & (dataset.excerpt == excerpt)
        & (dataset.session == session)
    ].reset_index()
    print(rows)
    for i, row in rows.iterrows():
        offset = row["start"]
        offset -= 1

        duration = row["end"] - offset
        print(row["file"])
        audio, sr = librosa.load(
            str(row["file"]), sr=SR, offset=offset, duration=duration, mono=False
        )
        audio /= np.abs(audio).max()
        scipy.io.wavfile.write(f"../data/raw/{P}-{V}-{E}.{i}.wav", sr, audio.T)

        audio = cut.cut(audio, sr, excerpt)
        scipy.io.wavfile.write(f"../data/auto-cut/{P}-{V}-{E}.{i}.wav", sr, audio.T)
