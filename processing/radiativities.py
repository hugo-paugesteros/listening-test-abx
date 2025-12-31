import pandas as pd
import xarray as xr
from frf.dataset.synthetic import load_radiativity, load_excerpt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib

DATA_DIR = pathlib.Path("/home/hugo/Thèse/Data")
CONFIG = {
    "sr": 48000,
    "violins": ["Klimke", "Levaggi", "Stoppani"],
    "paths": {
        "strings": DATA_DIR / "Synthétiques/string",
        "measurements": DATA_DIR / "CNSM/AfterOpening_CNSM",
        "mobilities": DATA_DIR / "Synthétiques/mobilities",
    },
}
records = []
for violin in CONFIG["violins"]:
    violin_path = CONFIG["paths"]["measurements"] / violin
    pattern = "* 0[0-9] [HV][VH]_Cplx.tsv"
    # pattern = "* 0[0-9] [H]_001_trf.tsv"

    for file in sorted(violin_path.rglob(pattern)):
        measure_type = file.stem[-9:-8]
        measure_n = file.stem[-11:-10]
        records.append(
            {
                "path": file.parent,
                "filename": str(file),
                "violin": violin,
                "sr": CONFIG["sr"],
            }
        )
radiativities_md = pd.DataFrame(records)
# radiativities_md = pd.read_pickle(
#     "/home/hugo/Thèse/frf/data/processed/radiativities.pkl"
# )

radiativities_md = radiativities_md[
    radiativities_md.violin.isin(["Klimke", "Levaggi", "Stoppani"])
]
radiativities_md.replace(
    {"Klimke": "VA", "Levaggi": "VB", "Stoppani": "VC"}, inplace=True
)

radiativities = []
for radiativity_row in radiativities_md.itertuples():
    radiativity_signal = load_radiativity(radiativity_row.filename)
    radiativities.append(radiativity_signal.Y)

radiativities = xr.DataArray(
    radiativities,
    dims=["measurement", "frequency"],
    coords={
        "measurement": radiativities_md.index,
        "frequency": np.arange(radiativity_signal.Y.shape[0])
        / radiativity_signal.Y.shape[0]
        * (48000 // 2),
        "violin": ("measurement", radiativities_md["violin"]),
    },
)
radiativities_db = 20 * np.log10(np.abs(radiativities))
# radiativities_db -= radiativities_db.max(axis=1)
df = (
    radiativities_db.isel(frequency=slice(200, 5000))
    .to_dataframe(name="amplitude_db")
    .reset_index()
)
df["measurement"] = df["measurement"].astype(str)
print(df[df.measurement == 5])

sns.relplot(
    data=df,
    x="frequency",
    y="amplitude_db",
    hue="measurement",
    row="violin",
    kind="line",
    height=3,
    aspect=2,
    estimator=None,
    units="measurement",
)
plt.xticks([200, 500, 1000, 5000])
plt.xscale("log")
plt.show()
