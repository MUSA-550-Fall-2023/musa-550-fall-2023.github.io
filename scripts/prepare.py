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

# Get the current week
current_week = variables["current_week"]
if current_week == "None":
    current_week = 0
else:
    current_week = int(current_week)

# Load the schedule data
topics = pd.read_csv(root_dir / "data" / "week-topics.csv").sort_values(
    "week", ascending=True
)


# Calculate the contents
contents = ["content/index.qmd"]
for i, r in topics.iterrows():
    # Only show content for weeks we've posted
    if r["week"] > current_week:
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
