from amzn_wl.entities import wishlists


class TestWishlist:
    def test_to_dict(self):
        wishlist = wishlists.Wishlist("wid", "site.com", "name")

        result = wishlist.to_dict()

        assert result == {
            "wishlist_id": "wid",
            "hostname": "site.com",
            "name": "name",
            "url": "https://site.com/hz/wishlist/ls/wid",
        }


class TestExtractHostnameAndWishlistId:
    def test(self):
        hostname = "www.amazon.com"
        wishlist_id = "WF1YPOU6BH4B"
        url = f"https://{ hostname }/hz/wishlist/ls/{ wishlist_id }"

        result = wishlists.extract_hostname_and_wishlist_id(url)

        assert result == (hostname, wishlist_id)
