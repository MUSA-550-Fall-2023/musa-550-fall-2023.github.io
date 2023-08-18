import pandas as pd

import utils, config, icons


def _add_assignment_row(html, data, disabled, include_date=False):
    """Add a row for an assignment."""

    # Add row
    html.append("<tr>")

    # Col #1: Empty
    html.append("""<td class="col-week"></td>""")

    # Col #2: Date
    if not include_date:
        html.append("""<td class="col-lecture"></td>""")
    else:
        html.append(
            f"""
            <td class="col-lecture">
                <span class="content-class">{data["date_formatted"]}</span>
            </td>
            """
        )

    # Col #3: Text description
    text = f"{data['description']} {data['task']}"
    if data["task"] == "due":
        icon = icons.get_hw_due(sizing="fa-sm")
    else:
        icon = icons.get_hw_assigned(sizing="fa-sm")

    html.append(
        f"""
        <td class="col-lecture">
            <span class="assignment-icon-{data['task']}">{icon}</span>
            <span class="content-class content-assignment">{text}</span>
        </td>
        """
    )

    # Col #4: Github repo link
    url = f"https://github.com/{config.GITHUB_ORG}/{data['slug']}"
    html.append(
        f"""
        <td class="col-repo">
            <a class="content-repo {disabled}" href="{url}">
                <i class="fa-brands fa-github fa-lg"></i>
            </a>
        </td>
        """
    )

    # End
    html.append("</tr>")

    return html


def _add_lecture_cells(html, data, assignments, lecture_number, current_lecture):
    """Add cells for date, static slides, interactive slides."""

    # Get week number
    week_number = int(lecture_number[:-1])

    # Get the disabled class
    disabled = utils.get_disabled_class_by_lecture(
        lecture_number=lecture_number, current_lecture=current_lecture
    )

    # Cell #1: empty
    html.append('<td class="col-week"></td>')

    # Cell #2: Formatted date
    html.append(
        f"""
      <td class="col-lecture">
        <span class="content-class">{data["date_formatted"]}</span>
      </td>"""
    )

    # Cell #3: Lecture number
    html.append(
        f"""
      <td class="col-lecture">
        <span class="content-class">Lecture {lecture_number}</span>
      </td>"""
    )

    # Cell #4: Github repo link
    url = f"https://github.com/{config.GITHUB_ORG}/week-{week_number}"
    html.append(
        f"""
        <td class="col-repo">
            <a class="content-repo {disabled}" href="{url}">
                <i class="fa-brands fa-github fa-lg"></i>
            </a>
        </td>
        """
    )

    # Cell #5: Static cells
    html.append(
        f"""
        <td class="col-slides-static">
            <a class="content-slides-static {disabled}" href="/content/week-{week_number}/lecture-{lecture_number}.html">
                <i class="fa-solid fa-book-open-reader fa-lg"></i>
            </a>
        </td>
        """
    )

    # Cell #6: Interactive cells
    url = utils.get_binder_url(lecture_number)
    html.append(
        f"""
        <td class="col-slides-binder">
            <a class="content-slides-binder {disabled}" href="{url}">
                <img src="/files/binder-favicon.webp"/>
            </a>
        </td>
        """
    )
    html.append("</tr>")

    # Check for assignments and add row for each task
    hw = assignments.query(f"date_formatted == '{data['date_formatted']}'")
    if len(hw):
        for _, row in hw.iterrows():
            html = _add_assignment_row(html, row, disabled, include_date=False)

    return html


def _load_schedule_data():
    """Load the formatted schedule data."""

    # Load the schedule data
    dates = utils.load_data("schedule-dates.csv")
    topics = utils.load_data("schedule-topics.csv")

    # Merge and return
    return (
        dates.merge(topics, on="week")
        .assign(
            date=lambda df: pd.to_datetime(df.date),
            date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
        )
        .sort_values("class_number", ascending=True)
    )


def create_table():
    """Create the schedule HTML table."""

    # Get the schedule data
    data = _load_schedule_data()

    # Get info for the assignments
    assignments = utils.load_data("assignments.csv").assign(
        date=lambda df: pd.to_datetime(df.date),
        date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
    )

    # Get current lecture/week
    current_week = utils.get_current_week()
    current_lecture = utils.get_current_lecture()

    # Initialize table
    table = []

    # Add table class
    table.append(
        '<table class="table schedule-table table-borderless table-responsive">'
    )

    # Add thead
    headers = ["", "", "", "Github Repo", "HTML Slides", "Executable Slides"]
    table += ["<thead>", "<tr>"]
    for header in headers:
        table += [f"<th>{header}</th>"]
    table += ["</tr>", "</thead>"]

    # Add tbody
    table += ["<tbody>"]

    # Group by week and add lecture info
    for (week, topic), group in data.groupby(["week", "topic"], sort=False):
        # Is the week disabled?
        disabled = "disabled" if current_week < week else ""

        # Add week header row
        table.append('<tr class="week-header-row">')

        # Week number
        table.append(
            f"""
            <td class="col-week">
                <span class="content-week">Week {week}</span>
            </td>"""
        )

        # Topic
        table.append(
            f"""
            <td colspan="5" class="col-topic">
            <a class="content-topic {disabled}" href="/content/week-{week}">
                {topic}
            </a>
            </td>"""
        )
        table.append("</tr>")  # End week header row

        # Add the info for A lecture
        table.append("<tr>")
        table = _add_lecture_cells(
            html=table,
            data=group.iloc[0],
            assignments=assignments,
            lecture_number=f"{week}A",
            current_lecture=current_lecture,
        )

        # Do the "B" lecture too
        table.append('<tr class="lecture-row">')
        table = _add_lecture_cells(
            html=table,
            data=group.iloc[1],
            assignments=assignments,
            lecture_number=f"{week}B",
            current_lecture=current_lecture,
        )

    # Add header row for final project
    table.append(
        """
        <tr class="week-header-row">
            <td class="col-week" colspan="6">
                <span class="content-week">Finals period</span>
            </td>
        </tr>
        """
    )

    # Add row for final project task
    table = _add_assignment_row(
        html=table,
        data=assignments.query("slug == 'final-project'").squeeze(),
        disabled="",
        include_date=True,
    )

    table += ["</tbody>", "</table>"]
    table = "\n".join(table)

    return table
