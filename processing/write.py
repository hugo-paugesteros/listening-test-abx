import os
import pandas as pd
import scipy.io
import librosa

dataset = pd.read_pickle(
    "/home/hugo/Thèse/identification/data/processed/dataset_cnsm.pkl"
)
dataset = dataset[
    (dataset.session == 3)
    & (dataset.player == "SMD")
    & (dataset.violin == "A")
    & (dataset.extract.isin(["sibelius", "glazounov2", "tchai"]))
].drop_duplicates(subset=["player", "violin", "extract", "session"])
dataset.rename(columns={"extract": "excerpt"}, inplace=True)
dataset.excerpt.replace({"sibelius": "sibelius2"}, inplace=True)

print(dataset)

if not os.path.exists("data/excerpts"):
    os.makedirs("data/excerpts")

for i, row in dataset.iterrows():
    offset = row["start"]
    offset -= 1
    duration = row["end"] - offset

    audio, sr = librosa.load(
        str(row["file"]), sr=None, offset=offset, duration=duration, mono=False
    )
    audio /= audio.max()
    scipy.io.wavfile.write(
        f"data/excerpts/{row.player}-{row.violin}-{row.excerpt}.wav", sr, audio.T
    )
