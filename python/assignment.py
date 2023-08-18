import pandas as pd
from IPython.core.display import HTML

import utils, config, icons


def create_schedule_table():
    """Create the HTML for the summary assignment table."""

    # Initialize the table
    table = []

    # Add the table class
    table.append(
        '<table class="table assignment-table table-responsive">',
    )

    # Add thead
    table += ["<thead>", "<tr>"]
    table += [
        "<th></th>",
        f"""<th>
                <span class="assignment-icon-assigned">
                    {icons.get_hw_assigned(sizing="fa-sm")}
                </span>
                <span>Assigned on</span>
                </th>""",
        f"""<th>
                <span class="assignment-icon-due">
                    {icons.get_hw_due(sizing="fa-sm")}
                </span>
                <span>Due on</span>
                </th>""",
    ]
    table += ["</tr>", "</thead>"]

    # Load the data
    assignments = utils.load_data("assignments.csv").assign(
        date=lambda df: pd.to_datetime(df.date),
        date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
    )
    slugs = assignments["slug"].drop_duplicates()

    # Add tbody
    table += ["<tbody>"]
    for slug in slugs:
        # Trim
        data = assignments.query(f"slug == '{slug}'")

        # Row start
        table.append("<tr>")

        # Description
        table.append(f'<td>{data.iloc[0]["description"]}</td>')

        # Do each task
        for task in ["assigned", "due"]:
            data = assignments.query(f"slug == '{slug}' and task == '{task}'").squeeze()
            if len(data):
                table.append(f'<td>{data["date_formatted"]}</td>')
            else:
                table.append("<td></td>")

        table.append("</tr>")

    table += ["</tbody>", "</table>"]
    table = "\n".join(table)

    return table


def create_header(slug):
    """Create the HTML for the header on the assignment page."""

    # Load the data
    data = (
        utils.load_data("assignments.csv")
        .assign(
            date=lambda df: pd.to_datetime(df.date),
            date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
        )
        .query(f"slug == '{slug}'")
    )

    # Get the github classroom link from the data
    classroom_links = data["classroom_link"].dropna().drop_duplicates()
    if len(classroom_links):
        classroom_link = classroom_links.squeeze()
        disabled = ""
    else:
        classroom_link = None
        disabled = "disabled"

    # Store different lines of html
    html = []

    # Initialize the header
    html.append('<div class="assignment-header">')

    # Due the assigned and due dates
    for task in ["assigned", "due"]:
        # Get the data
        df = data.query(f"task == '{task}'").squeeze()

        if len(df):
            if task == "due":
                text = f"Due on {df['date_formatted']} at 11:59 PM"
                icon = f"""
                        <span class="assignment-icon-due">
                            {icons.get_hw_due(sizing="fa-sm")}
                        </span>
                        """
            else:
                text = f"Assigned on {df['date_formatted']}"
                icon = f"""
                        <span class="assignment-icon-assigned">
                            {icons.get_hw_assigned(sizing="fa-sm")}
                        </span>
                        """

            html.append(
                f"""
                        <div>
                            {icon}
                        <span>{text}</span>
                        </div>"""
            )

    html.append("</div>")

    # Now do the github links
    html.append('<div class="assignment-header mt-2">')

    # Do the Github repo
    url = f"https://github.com/{config.GITHUB_ORG}/{slug}"
    html.append(
        f"""
    <div class="assignment-page-repo">
        <i class="fa-brands fa-github fa-sm"></i>
        &nbsp;
        <span>View materials:</span>
        &nbsp;
        <a class="{disabled}" href="{url}">
            {config.GITHUB_ORG}/{slug}
        </a>
    </div>"""
    )

    html.append(
        f"""
    <div class="assignment-page-repo">
        <i class="fa-brands fa-github fa-sm"></i>
        &nbsp;
        <span>Submission link:</span>
        &nbsp;
        <a class="{disabled}" href="{classroom_link}">
            GitHub classroom
        </a>
    </div>"""
    )

    html.append("</div>")

    # Check current date
    if classroom_link is None:
        html.append(
            """<div class="assignment-check-back">Check back after the homework has been assigned for details.</div>"""
        )

    return HTML("\n".join(html))
