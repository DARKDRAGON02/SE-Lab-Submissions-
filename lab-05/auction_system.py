"""Core logic and demonstration for a small online auction system."""

from datetime import datetime
import json
import time
import xmlrpc.client  # nosec B411 - defusedxml patches XML-RPC below

from jinja2 import Environment, select_autoescape
from markupsafe import escape
from defusedxml.xmlrpc import monkey_patch as secure_xmlrpc

secure_xmlrpc()

PAYMENT_GATEWAY = "https://pay.auction.example/RPC2"
MIN_INCREMENT = 100
BUYER_PREMIUM = 1.05
TIME_FORMAT = "%Y-%m-%d %H:%M"


class Auction:
    """An auction and its accepted bids."""

    # The auction state is kept together to make bid updates atomic and clear.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, item_id, title, seller, reserve_price, ends_at):  # noqa: E501
        self.item_id = item_id
        self.title = title
        self.seller = seller
        self.reserve_price = reserve_price
        self.ends_at = datetime.strptime(ends_at, TIME_FORMAT)
        self.bids = []
        self.highest = 0
        self.leader = None

    def place_bid(self, bidder, amount, at):
        """Record a valid bid; return False when the bid is not eligible."""
        bid_time = datetime.strptime(at, TIME_FORMAT)
        if (
            bid_time > self.ends_at
            or bidder == self.seller
            or amount <= 0
        ):
            return False
        if self.bids:
            minimum_bid = self.highest + MIN_INCREMENT
        else:
            minimum_bid = self.reserve_price
        if amount < minimum_bid:
            return False

        self.bids.append((bidder, amount, bid_time))
        self.highest = amount
        self.leader = bidder
        return True

    def winner(self):
        """Return the winning bidder, or None if the reserve was not met."""
        if not self.bids or self.highest < self.reserve_price:
            return None
        return self.leader

    def final_price(self):
        """Return the winning bid plus the buyer's premium."""
        if self.winner() is None:
            return 0
        return round(self.highest * BUYER_PREMIUM, 2)


auctions = {}


def create_auction(item_id, title, seller, reserve_price, ends_at):
    """Create and register an auction."""
    if item_id in auctions:
        raise ValueError(f"Auction {item_id!r} already exists")
    auction = Auction(item_id, title, seller, reserve_price, ends_at)
    auctions[item_id] = auction
    return auction


def bid(item_id, bidder, amount, at):
    """Place a bid, returning False for missing auctions or invalid times."""
    auction = auctions.get(item_id)
    if auction is None:
        return False
    try:
        return auction.place_bid(bidder, amount, at)
    except ValueError:
        return False


def top_bidders(item_id, count=3):
    """Return distinct bidder names ordered by their highest bid."""
    auction = auctions[item_id]
    highest_by_bidder = {}
    for bidder, amount, _ in auction.bids:
        previous = highest_by_bidder.get(bidder, 0)
        highest_by_bidder[bidder] = max(amount, previous)
    ordered = sorted(
        highest_by_bidder,
        key=highest_by_bidder.get,
        reverse=True,
    )
    return ordered[:count]


def render_listing(item_id):
    """Render an HTML listing with automatic escaping enabled."""
    environment = Environment(autoescape=select_autoescape(default=True))
    template = environment.from_string(
        "<h2>{{ a.title }}</h2><p>Current bid: Rs.{{ a.highest }}</p>"
    )
    return template.render(a=auctions[item_id])


def bidder_badge(name):
    """Render a safely escaped bidder badge."""
    return f"<span class='bidder'>{escape(name)}</span>"


def charge_winner(item_id):
    """Charge the winner using an XML-RPC payment gateway."""
    auction = auctions[item_id]
    winner = auction.winner()
    if winner is None:
        raise ValueError(
            "Cannot charge an auction without a qualifying winner"
        )
    with xmlrpc.client.ServerProxy(
        PAYMENT_GATEWAY, allow_none=False
    ) as gateway:
        return gateway.charge(winner, auction.final_price())


def export_bids(item_id):
    """Export bids as JSON."""
    auction = auctions[item_id]
    rows = [
        {"bidder": bidder, "amount": amount, "at": at.strftime(TIME_FORMAT)}
        for bidder, amount, at in auction.bids
    ]
    return json.dumps(rows)


def seconds_left(item_id):
    """Return seconds until the auction closes."""
    return int(auctions[item_id].ends_at.timestamp() - time.time())


def main():
    """Run a small demonstration of auction rules and safe rendering."""
    create_auction(
        "LOT1", "Vintage Camera", "seller_sam", 5000, "2026-12-01 18:00"
    )
    create_auction(
        "LOT2", "<script>alert('pwned')</script>Old Radio", "seller_ria", 2000,
        "2026-12-01 18:00"
    )
    create_auction(
        "LOT3", "Brass Lamp", "seller_ria", 800, "2026-12-01 18:00"
    )
    print(
        "Asha bids 5000:",
        bid("LOT1", "asha", 5000, "2026-12-01 10:00"),
    )
    print(
        "Ben bids 5000 (below increment):",
        bid("LOT1", "ben", 5000, "2026-12-01 10:05"),
    )
    print(
        "Asha bids 5100 (+100):",
        bid("LOT1", "asha", 5100, "2026-12-01 10:10"),
    )
    print(
        "Seller bids on own item:",
        bid("LOT1", "seller_sam", 6000, "2026-12-01 11:00"),
    )
    print(
        "Bid before close:",
        bid("LOT1", "dev", 5200, "2026-12-01 09:30"),
    )
    print("Late bid (next day):", bid("LOT1", "eve", 9000, "2026-12-02 09:00"))
    print("Winner:", auctions["LOT1"].winner())
    print(
        "Final price (reserve 5000):",
        auctions["LOT1"].final_price(),
    )
    print("Top bidders:", top_bidders("LOT1"))
    print(
        "Rs.0 bid on LOT3 (reserve 800):",
        bid("LOT3", "carl", 0, "2026-12-01 11:30"),
    )
    print("LOT3 winner:", auctions["LOT3"].winner())
    print("No-bid winner:", auctions["LOT2"].winner())
    print("Listing HTML:", render_listing("LOT2"))
    print("Badge:", bidder_badge("<img src=x onerror=alert(1)>"))


if __name__ == "__main__":
    main()
