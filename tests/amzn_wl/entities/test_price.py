from decimal import Decimal

from amzn_wl.entities.price import Price


class TestPrice:
    def test(self):
        price = Price("9.99", "$", "USD")
        assert price.value == Decimal("9.99")

    def test_parse_usd(self):
        price = Price.parse("Some $1,999.99 in sentence")
        assert price.value == Decimal("1999.99")
        assert price.currency == "$"
        assert price.currency_code == "USD"

    def test_parse_jpy(self):
        price = Price.parse("元の価格は￥1,999.99です")
        assert price.value == Decimal("1999.99")
        assert price.currency == "￥"
        assert price.currency_code == "JPY"
