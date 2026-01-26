import json
import shutil
import pathlib

with open("../public/cfg.json", "r") as file:
    data = json.load(file)

files = []
for test in data:
    files.append(test["A"])
    files.append(test["B"])
    files.append(test["X"][0])
    files.append(test["X"][1])

files = set(files)
print(files)
print(len(files))

for file in files:
    src = pathlib.Path("../data/normalized/") / pathlib.Path(file).name
    dst = pathlib.Path("../data/test_final/")
    print(src)
    print(dst)
    shutil.copy(src, dst)
