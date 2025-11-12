"""
smpub Publisher for Shop class.

This is ONLY the publisher - the actual Shop implementation is in sample_shop/.

Key points:
1. Shop is a standalone Python library (see ../sample_shop/)
2. This file just imports Shop and publishes it
3. smpub is a thin layer - Shop doesn't know about it

To use Shop without smpub, see:
- ../sample_shop/example_pythonic.py
- ../sample_shop/shop_usage.ipynb
"""

from smpub import Publisher
from examples.sample_shop import Shop


class PublishedShop(Publisher):
    """
    Publisher for Shop class.

    Notice how simple this is:
    1. Import Shop from sample_shop (standalone library)
    2. Instantiate it (normal Python object)
    3. Publish it (add CLI/HTTP layer)

    That's it! smpub is just a thin publishing layer.

    Note: We implement on_init() instead of __init__() to avoid calling super().
    Publisher.__init__() will call our on_init() after setting up the infrastructure.
    """

    def on_init(self):
        """Initialize and publish Shop components."""
        # Import and instantiate Shop - it's just a normal Python class
        shop = Shop()

        # Publish table managers for CLI/HTTP access
        self.publish("types", shop.types)
        self.publish("articles", shop.articles)
        self.publish("purchases", shop.purchases)


if __name__ == "__main__":
    app = PublishedShop()
    app.run()
