import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime

from pywebio import start_server, config
from pywebio.input import input_group, input, TEXT


@dataclass
class Visit:
    visitor: str
    visitee: str | None
    time: datetime


def get_visitees(db_conn: sqlite3.Connection) -> list[str]:
    with db_conn as db_transaction:
        visitee_rows = db_transaction.execute(
            "SELECT DISTINCT visitee FROM visits WHERE visitee IS NOT NULL"
        ).fetchall()
    return [row[0] for row in visitee_rows]


def get_visitors(db_conn: sqlite3.Connection) -> list[str]:
    with db_conn as db_transaction:
        visitor_rows = db_transaction.execute(
            "SELECT DISTINCT visitor FROM visits WHERE visitor IS NOT NULL"
        ).fetchall()
    return [row[0] for row in visitor_rows]


@config(title="Visitors")
def main():
    with closing(sqlite3.connect("visits.db")) as db_conn:
        previous_visitors = get_visitors(db_conn)
        previous_visitees = get_visitees(db_conn)

    visit_input = input_group(
        "New visit",
        [
            input(
                "Visitor",
                type=TEXT,
                datalist=previous_visitors,
                name="visitor",
                required=True,
            ),
            # Not required - a generic visit can occur, to no one in particular.
            input("Visitee", type=TEXT, datalist=previous_visitees, name="visitee"),
        ],
    )
    visitee = visit_input["visitee"] if len(visit_input["visitee"]) != 0 else None
    visit = Visit(visit_input["visitor"], visitee, datetime.now())
    # Next line is the standard lib's `sqlite3.connect`'s fault
    with closing(sqlite3.connect("visits.db")) as db_conn, db_conn as db_transaction:
        # TODO: Support multiple visitees
        db_transaction.execute(
            "INSERT INTO visits VALUES (?, ?, ?)",
            (visit.visitor, visit.visitee, visit.time.isoformat()),
        )
    print(f"{visit=}")


if __name__ == "__main__":
    start_server(main, port=8080, debug=True)
