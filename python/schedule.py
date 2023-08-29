import pandas as pd
import utils, config, icons
from datetime import datetime


def _add_assignment_row(html, data, disabled, group_dates):
    """Add a row for an assignment."""

    # Show the date?
    show_date = data["date_formatted"] not in group_dates

    # Add row
    html.append("<tr>")

    # Col #1: Empty
    html.append("""<td class="col-week"></td>""")

    # Col #2: Date
    if show_date:
        html.append(
            f"""
            <td class="col-lecture">
                <span class="content-class">{data["date_formatted"]}</span>
            </td>
            """
        )
    else:
        html.append(
            """
            <td class="col-lecture">
                <span class="content-class"></span>
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


def _add_lecture_row(html, data, lecture_number, group_dates, disabled):
    """Add cells for date, static slides, interactive slides."""

    # Show the date?
    show_date = data["date_formatted"] not in group_dates

    # Get week number
    week_number = utils.get_week_from_lecture_number(lecture_number)

    # New lecture row
    html.append("<tr class='lecture-row>")

    # Cell #1: empty
    html.append('<td class="col-week"></td>')

    # Cell #2: Formatted date
    if show_date:
        html.append(
            f"""
            <td class="col-lecture">
                <span class="content-class">{data["date_formatted"]}</span>
            </td>"""
        )
    else:
        html.append(
            """
            <td class="col-lecture">
                <span class="content-class"></span>
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

    return html


def _load_lecture_schedule(section_number):
    """Load the formatted schedule data for lectures."""

    # Load the schedule data
    dates = utils.load_data(
        f"{section_number}/lecture-dates.csv", dtypes={"class_number": str, "week": int}
    )

    # Merge and return
    return dates.assign(
        date=lambda df: pd.to_datetime(df.date),
        date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
    ).sort_values("class_number", ascending=True)


def _load_assignment_schedule(section_number):
    """Load the formatted schedule data for assignments."""

    schedule = utils.load_data(f"{section_number}/assignment-dates.csv").assign(
        date=lambda df: pd.to_datetime(df.date),
        date_formatted=lambda df: df.date.dt.strftime("%A, %B %-d"),
    )

    return schedule.merge(
        utils.load_data(f"{section_number}/assignment-details.csv"), on="slug"
    )


def create_table(section_number):
    """Create the schedule HTML table."""

    # Get the lecture schedule data
    lectures = _load_lecture_schedule(section_number)

    # Get info for the assignments
    hws = _load_assignment_schedule(section_number)

    # Combine the data
    data = (
        pd.concat([lectures.assign(order=1), hws.assign(order=2)], axis=0)
        .sort_values(["date", "order"], ascending=True)
        .assign(
            week=lambda df: df.week.fillna(method="ffill").astype(int),
            task=lambda df: df.task.fillna(""),
        )
    )

    # Get the topics
    topics = utils.load_data("week-topics.csv")
    data = data.merge(topics, on="week")

    # Get current week
    current_week = utils.get_current_week()

    # Get the latest_date
    if current_week is not None:
        latest_date = lectures.query(f"week == {current_week}")["date"].dropna().max()
    else:
        latest_date = datetime.today()

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
        disabled = "disabled" if current_week is None or current_week < week else ""

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

        # Dates in this group
        group_dates = []

        # Iterate over rows in group
        for _, row in group.iterrows():
            # Add row for lecture (only assignments have a task)
            if not row["task"]:
                table = _add_lecture_row(
                    html=table,
                    data=row,
                    lecture_number=row["class_number"],
                    group_dates=group_dates,
                    disabled="disabled" if row["date"] > latest_date else "",
                )
            # Add hw row
            else:
                table = _add_assignment_row(
                    html=table,
                    data=row,
                    disabled="" if row["live"] else "disabled",
                    group_dates=group_dates,
                )

            # Track the dates
            if row["date_formatted"] not in group_dates:
                group_dates.append(row["date_formatted"])

    # Close it out
    table += ["</tbody>", "</table>"]
    table = "\n".join(table)

    return table
