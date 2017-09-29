import json
x = []
with open("donotdo.txt", mode="r", encoding="utf8") as openfile:
    x = openfile.readlines()
with open("donotdo.json", encoding='utf-8', mode="w") as f:
            json.dump(x, f, indent=4,sort_keys=True,
                separators=(',',' : '))