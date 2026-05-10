from app.product_enricher import enrich_products
from app.product_search import search_products
from app.requirements_parser import parse_requirements
from app.recommender import recommend_best_product
from app.scorer import calculate_score


def main() -> None:
    user_query = (
        "Jeg vil have en robotstøvsuger med moppe, "
        "høj sugeevne, som kan klare måtter og undgå legetøj. "
        "Den må maks koste 5000 kr."
    )

    requirements = parse_requirements(user_query)

    products = enrich_products(search_products(
        "robotstøvsuger moppe obstacle avoidance høj sugeevne"
    ))

    best_product = recommend_best_product(products, requirements)

    if best_product is None:
        print("Ingen produkter fundet.")
        return

    print("Bedste match:")
    print(best_product)
    print(f"Score: {calculate_score(best_product, requirements)}/100")


if __name__ == "__main__":
    main()