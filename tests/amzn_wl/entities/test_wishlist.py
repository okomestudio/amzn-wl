from amzn_wl.entities.wishlist import Wishlist, extract_wishlist_id
from amzn_wl.entities.site import Site


class TestWishlist:
    def test_to_dict(self):
        site = Site("site.com")
        wishlist = Wishlist("wid", site, "name")

        result = wishlist.to_dict()

        assert result == {
            "wishlist_id": "wid",
            "site": {"hostname": "site.com"},
            "name": "name",
            "url": "https://site.com/hz/wishlist/ls/wid",
        }


class TestExtractWishlistId:
    def test(self):
        hostname = "www.amazon.com"
        wishlist_id = "WF1YPOU6BH4B"
        url = f"https://{ hostname }/hz/wishlist/ls/{ wishlist_id }"

        result = extract_wishlist_id(url)

        assert result == wishlist_id
