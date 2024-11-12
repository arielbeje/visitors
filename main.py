from pywebio import start_server, config
from pywebio.input import input_group, radio, checkbox


def get_visitees() -> list[str]:
    return ["visitee #1", "visitee #2"]


def get_visitors() -> list[str]:
    return ["visitor #1", "visitor #2"]


@config(title="Visitors")
def main():
    visit = input_group(
        "New visit",
        [
            # Radio - there can be only one visitor per visit
            radio("Visitor", get_visitors(), name="visitor", required=True),
            # Checkbox - there can be multiple visitees per visit
            checkbox("Visitee", get_visitees(), name="visitee"),
        ],
    )
    print(f"{visit=}")


if __name__ == "__main__":
    start_server(main, port=8080, debug=True)
