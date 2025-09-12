from yarl import URL


class ApiUrls:
    def __init__(self, base_url: URL) -> None:
        self.base_url = base_url

    def token(self) -> URL:
        return self.base_url / "v2/oauth/token"

    def suggest_cities(self) -> URL:
        return self.base_url / "v2/location/suggest/cities"

    def regions(self) -> URL:
        return self.base_url / "v2/location/regions"

    def postal_codes(self) -> URL:
        return self.base_url / "v2/location/postalcodes"

    def cities(self):
        return self.base_url / "v2/location/cities"

    def delivery_points(self):
        return self.base_url / "v2/deliverypoints"

    def tariff_list(self):
        return self.base_url / "v2/calculator/tarifflist"

    def tariff(self):
        return self.base_url / "v2/calculator/tariff"

    def tariff_and_service(self):
        return self.base_url / "v2/calculator/tariffAndService"

    def all_tariffs(self):
        return self.base_url / "v2/calculator/alltariffs"

    def restrictions(self):
        return self.base_url / "v2/international/package/restrictions"

    def orders(self):
        return self.base_url / "v2/orders"

    def order(self, uuid):
        return self.base_url / f"v2/orders/{uuid}"
