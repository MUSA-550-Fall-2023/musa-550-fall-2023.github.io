import yaml
import pandas as pd
from pyprojroot.here import here
from urllib.parse import urlencode
import config
import argparse

DEFAULT_SECTION_NUMBER = "401"


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


def get_current_lecture(section_number=DEFAULT_SECTION_NUMBER):
    """Get the current lecture from project variables."""

    variables = load_variables()
    current_lecture = variables["current_lecture"][section_number]
    if current_lecture == "None":
        return None
    return current_lecture


def get_week_from_lecture_number(lecture_number):
    """Return the week from the lecture number."""
    return int(lecture_number.replace("A", "").replace("B", ""))  # Drop the letter


def get_current_week(section_number=DEFAULT_SECTION_NUMBER):
    """Get the current week number from project variables."""

    # Get the current lecture
    current_lecture = get_current_lecture(section_number)
    if current_lecture is None:
        return None

    # Get the matching week number
    current_week = get_week_from_lecture_number(current_lecture)
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
