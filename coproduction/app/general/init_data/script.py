import json
import re

jsonData = {
    "phases": {},
    "assetTypes": []
}

with open('data.json') as json_file:
    data = json.load(json_file)
    
for phase in data:
    phaseTitle = phase["title"]
    phaseTitle = re.sub('[^a-zA-Z ]+', '', phaseTitle).strip().replace("  ", " ").replace(" ", "_").lower()
    jsonData["phases"][phaseTitle] = {}
    for objective in phase["children"]["attached"]:
        objectiveTitle = objective["title"]
        objectiveTitle = re.sub('[^a-zA-Z ]+', '', objectiveTitle).strip().replace("  ", " ").replace(" ", "_").lower()
        jsonData["phases"][phaseTitle][objectiveTitle] = {}
        for ques in objective["children"]["attached"]:
            title = ques["title"]
            for task in ques["children"]["attached"]:
                if not "." in title:
                    taskTitle = task["title"]
                    taskTitle = re.sub('[^a-zA-Z ]+', '', taskTitle).strip().replace("  ", " ").replace(" ", "_").lower()
                    if not "........" in taskTitle:
                        jsonData["phases"][phaseTitle][objectiveTitle][taskTitle] = []
                for asset in task["children"]["attached"]:
                    if not "." in title:
                        assetTitle = asset["title"].replace("\n", "")
                        type = assetTitle.split(" - ")[0]
                        if not "........" in assetTitle and type.isupper():
                            jsonData["phases"][phaseTitle][objectiveTitle][taskTitle].append(assetTitle)
                            if type not in jsonData["assetTypes"]:
                                jsonData["assetTypes"].append(type)


with open('cleaned.json', "w") as json_file:
    json_file.write(json.dumps(jsonData))
    