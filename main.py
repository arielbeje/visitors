import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime

from pywebio import start_server, config
from pywebio.input import input_group, input, TEXT
from pywebio.output import put_markdown, put_scope, put_table


@dataclass
class Visit:
    visitor: str
    visitee: str | None
    time: datetime

    def to_table_row(self) -> dict[str, str]:
        return {
            "Visitor": self.visitor,
            "Visitee": self.visitee
            if self.visitee is not None
            else "<No one in particular>",
            "Time": self.time.isoformat(),
        }


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


def get_visits(db_conn: sqlite3.Connection) -> list[Visit]:
    with db_conn as db_transaction:
        visit_rows = db_transaction.execute("SELECT * FROM visits")
    visits = [
        Visit(row[0], row[1], datetime.fromisoformat(row[2])) for row in visit_rows
    ]
    visits.sort(key=lambda visit: visit.time, reverse=True)
    return visits


@config(title="Visitors")
def main():
    with closing(sqlite3.connect("visits.db")) as db_conn:
        previous_visitors = get_visitors(db_conn)
        previous_visitees = get_visitees(db_conn)
        previous_visits = get_visits(db_conn)

    put_scope(
        "previous_visits",
        [
            put_markdown("# Previous Visits"),
            put_table(list(map(Visit.to_table_row, previous_visits))),
        ],
    )

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
