from langcodes import Language

corrections = {
    "pt br": "pt",
}


def land_code_to_name(value):
    if not value:
        return None
    if isinstance(value, str):
        if value in corrections:
            value = corrections[value]
        value = [value]

    results = list()
    for entry in value:
        results.append(
            Language.make(language=entry.lower().replace(" ", "_")).display_name()
        )

    return results
