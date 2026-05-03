from data.neo4j_seed import build_mock_products, build_mock_purchases


class TestNeo4jSeed:

    def test_build_mock_products_default_count(self):
        products = build_mock_products()

        assert len(products) == 15
        assert all("id" in product for product in products)
        assert all("name" in product for product in products)
        assert all("type" in product for product in products)
        assert all("price" in product for product in products)


    def test_build_mock_purchases_has_expected_volume_and_totals(self):
        products = build_mock_products()
        purchases, contains_items = build_mock_purchases(products=products, purchase_count=1000, seed=7)

        assert len(purchases) == 1000
        assert len(contains_items) >= 1000

        totals_by_purchase = {}
        for item in contains_items:
            totals_by_purchase.setdefault(item["purchase_id"], 0.0)
            totals_by_purchase[item["purchase_id"]] += item["line_total"]

        for purchase in purchases:
            expected_total = round(totals_by_purchase[purchase["id"]], 2)
            assert purchase["total_amount"] == expected_total

