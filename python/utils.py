import yaml
import pandas as pd
from pyprojroot.here import here
from urllib.parse import urlencode
import config


def get_disabled_class_by_lecture(current_lecture, lecture_number):
    """Get the disabled flag for each lecture."""

    # Get weeks from lecture numbers
    week_number = int(lecture_number[:-1])
    current_week = int(current_lecture[:-1])

    disabled = ""
    if week_number > current_week:
        disabled = "disabled"
    elif (
        week_number == current_week
        and lecture_number.endswith("B")
        and current_lecture.endswith("A")
    ):
        disabled = "disabled"

    return disabled


def get_binder_url(lecture_number):
    """Get the Binder url for a lecture."""

    # The repo where the environment is installed
    ENV_REPO = f"{config.GITHUB_ORG}/python-environment"

    # The content for this week
    week_number = int(lecture_number[:-1])
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


def load_data(filename):
    """Load data from CSV file in the data/ folder."""

    root_dir = here()
    return pd.read_csv(root_dir / "data" / filename)


def get_current_lecture():
    """Get the current lecture from project variables."""

    variables = load_variables()
    current_lecture = variables["current_lecture"]
    return current_lecture


def get_current_week():
    """Get the current week number from project variables."""

    current_lecture = get_current_lecture()
    current_week = int(current_lecture[:-1])  # Drop the letter
    return current_week
