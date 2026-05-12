import json
from pathlib import Path


def main() -> None:
    cache_files = list(Path("cache").glob("*.json"))

    if not cache_files:
        print("No cache files found.")
        return

    for index, cache_file in enumerate(cache_files):
        print(f"{index}: {cache_file}")

    selected_index = 0
    cache_file = cache_files[selected_index]

    with open(cache_file, encoding="utf-8") as file:
        data = json.load(file)

    results = data.get("shopping_results", [])

    if not results:
        print("No shopping_results found.")
        return

    first_item = results[0]

    print()
    print(f"Cache file: {cache_file}")
    print()
    print("Available fields:")
    for key in first_item.keys():
        print(f"- {key}")

    print()
    print("Possible link values:")
    for key in [
        "link",
        "product_link",
        "serpapi_product_api",
        "merchant_link",
        "seller_link",
        "source_link",
        "multiple_sources",
        "serpapi_immersive_product_api",
    ]:
        print(f"{key}: {first_item.get(key)}")

    print()
    print("First item full JSON:")
    print(json.dumps(first_item, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
