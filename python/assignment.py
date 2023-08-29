import pandas as pd
import utils, config, icons


def create_schedule_table(section_number):
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
    assignments = utils.load_data(f"{section_number}/assignment-dates.csv").assign(
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


def create_header(slug, section_number):
    """Create the HTML for the header on the assignment page."""

    # Assignments: live/classroom links
    assignments = (
        utils.load_data(f"{section_number}/assignment-details.csv")
        .query(f"slug == '{slug}'")
        .squeeze()
        .fillna("")
    )

    # Load the data and trim by slug
    schedule = (
        utils.load_data(f"{section_number}/assignment-dates.csv")
        .assign(
            date=lambda df: pd.to_datetime(df.date),
            date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
        )
        .query(f"slug == '{slug}'")
    )

    # Is this disabled?
    disabled = "" if assignments["live"] else "disabled"

    # Store different lines of html
    html = []

    # Initialize the header
    html.append('<div class="assignment-header">')

    # Due the assigned and due dates
    for task in ["assigned", "due"]:
        # Get the data
        df = schedule.query(f"task == '{task}'").squeeze()

        if len(df):
            if task == "due":
                text = f"Due on {df['date_formatted']} at 11:59 PM"
                icon = f"""<span class="assignment-icon-due">{icons.get_hw_due(sizing="fa-sm")}</span>"""
            else:
                text = f"Assigned on {df['date_formatted']}"
                icon = f"""<span class="assignment-icon-assigned">{icons.get_hw_assigned(sizing="fa-sm")}</span>"""

            html.append(f"""<div>{icon}<span>{text}</span></div>""")
    html.append("</div>")

    # Now do the github links
    html.append('<div class="assignment-header mt-2 mb-5">')

    # Do the Github repo
    url = f"https://github.com/{config.GITHUB_ORG}/{slug}"
    html.append(
        f"""<div class="assignment-page-repo"><i class="fa-brands fa-github fa-sm"></i>&nbsp;<span>View materials:</span>&nbsp;<a class="{disabled}" href="{url}">{config.GITHUB_ORG}/{slug}</a></div>"""
    )

    # Get the classroom link
    classroom_link = assignments["classroom_link"]
    if not classroom_link:
        disabled = "disabled"

    html.append(
        f"""<div class="assignment-page-repo"><i class="fa-brands fa-github fa-sm"></i>&nbsp;<span>Submission link:</span>&nbsp;<a class="{disabled}" href="{classroom_link}">GitHub classroom</a></div>"""
    )

    html.append("</div>")
    return "\n".join(html)
