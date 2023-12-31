import yaml
import pandas as pd
from pyprojroot.here import here
from urllib.parse import urlencode
import config
import argparse


def get_binder_url(lecture_number):
    """Get the Binder url for a lecture."""

    # The repo where the environment is installed
    ENV_REPO = f"{config.GITHUB_ORG}/python-environment"

    # The content for this week
    week_number = get_week_from_lecture_number(lecture_number)
    WEEK_REPO = f"https://github.com/{config.GITHUB_ORG}/week-{week_number}"

    # Filename
    path = f"week-{week_number}/lecture-{lecture_number}.ipynb"

    # Binder service
    BINDER_URL = "https://mybinder.org/v2/gh"

    # Encode the git pull params first
    git_pull_params = {
        "repo": WEEK_REPO,
        "urlpath": f"lab/tree/{path}",
        "branch": "main",
    }

    # Encode the binder params nopw
    params = urlencode({"urlpath": f"git-pull?{urlencode(git_pull_params)}"})

    # Return the full link
    return f"{BINDER_URL}/{ENV_REPO}/main?{params}"


def load_variables():
    """Load the variables from _variables.yml."""

    root_dir = here()
    return yaml.load((root_dir / "_variables.yml").open("r"), yaml.Loader)


def load_data(filename, dtypes={}):
    """Load data from CSV file in the data/ folder."""

    root_dir = here()
    return pd.read_csv(root_dir / "data" / filename, dtype=dtypes)


def get_week_from_lecture_number(lecture_number):
    """Return the week from the lecture number."""
    return int(lecture_number[:-1])  # Drop the A/B letter


def get_current_week():
    """Get the current week number from project variables."""

    # Load the variables
    variables = load_variables()
    current_week = variables["current_week"]

    # Check for None
    if current_week == "None":
        return None
    return current_week


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get the Binder URL for the specified lecture."
    )
    parser.add_argument(
        "week",
        type=str,
        help="The lecture number to get the Binder URL for.",
    )
    args = parser.parse_args()

    print(get_binder_url(args.week))
