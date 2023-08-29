import pandas as pd
from IPython.core.display import HTML

import utils, config

DEFAULT_SECTION_NUMBER = "401"


def create_header(slug):
    """
    Create the HTML for the header on each weekly content page.

    Parameters
    ----------
    slug : str
        This is extracted from the content folder name, e.g., "week-1".
    """

    # Get week number from slug
    week_number = int(slug.split("-")[-1])

    # Get current week
    current_week = utils.get_current_week()

    # Load the schedule dates
    data = utils.load_data(f"{DEFAULT_SECTION_NUMBER}/lecture-dates.csv").assign(
        date=lambda df: pd.to_datetime(df.date)
    )

    # Get the dates
    dates = data.query(f"week == {week_number}")["date"].dt.strftime("%b. %-d")

    # Initialize html
    html = []

    # Add subtitle with dates
    html.append(
        f'<div class="content-dates">Content for lectures {week_number}A and {week_number}B</div>'
    )

    # Now do the callout box
    html.append('<div class="content-header mt-2">')

    # Do the Github repo
    url = f"https://github.com/{config.GITHUB_ORG}/{slug}"
    html.append(
        f"""
        <div class="content-page-repo">
            <i class="fa-brands fa-github"></i>
            &nbsp;
            <span>View materials:</span>
            &nbsp;
            <a href="{url}">{config.GITHUB_ORG}/{slug}</a>
        </div>"""
    )

    # Are the disabled?
    disabled = "disabled" if week_number > current_week else ""

    # Lecture tags
    lectureA = f"{week_number}A"
    lectureB = f"{week_number}B"

    # Static slides
    html.append(
        f"""
        <div class="content-page-repo">
            <i class="fa-solid fa-book-open-reader"></i>
            &nbsp;
            <span>HTML slides:</span>
            &nbsp;
            <a class="{disabled}" href="./lecture-{lectureA}.html">
                Lecture {lectureA}
            </a>
            &nbsp;
            <a class="{disabled}" href="./lecture-{lectureB}.html">
                Lecture {lectureB}
            </a>
        </div>
        """
    )

    # Interactive slides
    html.append(
        f"""
        <div class="content-page-repo">
            <img class="binder-favicon" src="/files/binder-favicon.webp"></img>
            &nbsp;
            <span>Executable slides:</span>
            &nbsp;
            <a class="{disabled}" href="{utils.get_binder_url(lectureA)}">
                Lecture {lectureA}
            </a>
            &nbsp;
            <a class="{disabled}" href="{utils.get_binder_url(lectureB)}">
                Lecture {lectureB}
            </a>
        </div>
        """
    )

    html.append("</div>")
    return HTML("\n".join(html))
