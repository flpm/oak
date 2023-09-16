from rich import print
from rich.prompt import Prompt


def flat_hierarchy(node):
    results = set()
    for key, value in node.items():
        results.add(key)
        if value:
            results = results.union(
                {f"{key}.{entry}" for entry in flat_hierarchy(value)}
            )
    return results


def input_loop(valid_options, prompt="Add tag: "):
    line = None
    tags = set()
    new_valid_options = set()
    while line != "":
        line = input(prompt)
        if not line:
            print("")
        if line == "list":
            print(f"Current tags: {tags}")
        else:
            if line != "":
                if line in valid_options:
                    tags.add(line)
                    print(f"Current tags: {tags}")
                else:
                    if line.startswith("keyword."):
                        tags.add(line)
                        new_valid_options.add(line)
                    else:
                        print(f'(!) tag "{line}" does not exist')
                        options = list()
                        if len(line) >= 5:
                            options = [i for i in valid_options if line in i]
                        if options:
                            print(f"    {options[:5]}")
    return (tags, new_valid_options)


def confirm_loop(valid_options=("y", "n"), prompt="Are you sure?", default="n"):
    option = Prompt.ask(prompt, choices=valid_options, default=default)
    return option
