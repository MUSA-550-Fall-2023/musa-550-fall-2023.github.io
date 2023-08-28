import yaml
from pyprojroot import here
import pandas as pd
import os

if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
    exit()

# Load config
root_dir = here()
config_path = root_dir / "_quarto.yml"
config = yaml.load(config_path.open("r"), yaml.Loader)

# Load variables
variables = yaml.load((root_dir / "_variables.yml").open("r"), yaml.Loader)
current_lecture = variables["current_lecture"]["401"]
if current_lecture == "None":
    current_week = 0
else:
    current_week = int(current_lecture[:-1])

# Load the schedule data
dates = pd.read_csv(root_dir / "data" / "401" / "lecture-dates.csv")
topics = pd.read_csv(root_dir / "data" / "week-topics.csv")

# Merge
data = dates.merge(topics, on="week").sort_values("class_number", ascending=True)

# Calculate the contents
contents = ["content/index.qmd"]
for i, r in data.drop_duplicates(subset=["week"]).iterrows():
    # Only show content for weeks we've posted
    if r["week"] > current_week:
        continue
    elif (
        r["week"] == current_week
        and r["class_number"].endswith("B")
        and current_lecture.endswith("A")
    ):
        continue

    # Add the week
    contents.append(
        {
            "text": f"{r['week']}. {r['topic']}",
            "file": f"content/week-{r['week']}/index.qmd",
        }
    )

# Update the config
config["website"]["sidebar"][0]["contents"] = contents

# Save it
yaml.dump(config, config_path.open("w"))
