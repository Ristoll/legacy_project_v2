"""Product analytics and ranking functions."""

from typing import Any, Dict


def get_top_products(
    data: list[Dict[str, Any]],
    n: int = 10,
    sort_by: str = "revenue"
) -> list[Dict[str, Any]]:
    """Return the top N products sorted by the selected metric."""
    products = {}

    for item in data:
        product_id = item.get("product_id")

        if product_id not in products:
            products[product_id] = {
                "id": product_id,
                "name": item.get("product_name", "unknown"),
                "revenue": 0,
                "units": 0,
                "orders": 0
            }
        products[product_id]["revenue"] = products[product_id]["revenue"] + item.get("amount", 0)
        products[product_id]["units"] = products[product_id]["units"] + item.get("qty", 0)
        products[product_id]["orders"] = products[product_id]["orders"] + 1
    product_list = list(products.values())
    product_list.sort(key=lambda product: product[sort_by], reverse=True)
    return product_list[:n]
