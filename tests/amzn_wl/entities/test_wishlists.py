from amzn_wl.entities import wishlists


class TestExtractWishlistIdFromUrl:
    def test(self):
        expected = "WF1YPOU6BH4B"
        url = f"https://www.amazon.com/hz/wishlist/ls/{expected}"

        wishlist_id = wishlists.extract_wishlist_id_from_url(url)

        assert wishlist_id == expected
