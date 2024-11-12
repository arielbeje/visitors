from dataclasses import dataclass
from datetime import datetime

from pywebio import start_server, config
from pywebio.input import input_group, input, TEXT


@dataclass
class Visit:
    visitor: str
    visitee: str | None
    time: datetime


def get_visitees() -> list[str]:
    return ["visitee #1", "visitee #2"]


def get_visitors() -> list[str]:
    return ["visitor #1", "visitor #2"]


@config(title="Visitors")
def main():
    visit_input = input_group(
        "New visit",
        [
            input(
                "Visitor",
                type=TEXT,
                datalist=get_visitors(),
                name="visitor",
                required=True,
            ),
            # Not required - a generic visit can occur, to no one in particular.
            input("Visitee", type=TEXT, datalist=get_visitees(), name="visitee"),
        ],
    )
    visitee = visit_input["visitee"] if len(visit_input["visitee"]) != 0 else None
    visit = Visit(visit_input["visitor"], visitee, datetime.now())
    print(f"{visit=}")


if __name__ == "__main__":
    start_server(main, port=8080, debug=True)
