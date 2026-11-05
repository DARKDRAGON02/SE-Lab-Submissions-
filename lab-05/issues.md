# Static analysis findings and fixes

Baseline findings were collected from the original `auction_system.py` with
Pylint 4.1.3, Bandit 1.9.4, and Flake8 7.4.1. Line numbers below refer to the
original file.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| XML-RPC parser may process unsafe XML (B411) | Security, high | 4 | Bandit flags `xmlrpc.client` because XML-RPC responses can contain unsafe XML. | Apply `defusedxml.xmlrpc.monkey_patch()` before creating XML-RPC proxies; retain the import with a narrowly scoped Bandit suppression documenting that mitigation. |
| Unescaped HTML in listing and badge | Security, high | 68, 72 | `autoescape=False` and raw `Markup` concatenation let a title or bidder name inject HTML/script. | Enable Jinja autoescaping and escape bidder names with MarkupSafe. |
| Broad exception handler | Reliability | 48–50 | `except Exception` hides programming and runtime failures as ordinary rejected bids. | Look up missing auctions explicitly and catch only invalid date parsing. |
| Reserve and minimum increment are ignored | Functional bug | 24–27, 34 | A zero bid can lead an auction, ties are accepted, and reserve price has no effect on the winner or price. | Require the reserve for the first bid and a full `MIN_INCREMENT` for later bids; determine winners and final price only when reserve is met. |
| Seller can bid on own item | Functional bug | 24–27 | No check prevents the seller from bidding on their own listing. | Reject bids when the bidder matches the seller. |
| Auction times compared as strings | Functional bug | 22, 93–95 | Variable-width date text such as `9:30` is parsed inconsistently, and a time string can be compared lexicographically. | Parse bid and closing times once with the same explicit format, then compare `datetime` values. |
| Pylint quality/style findings | Quality | Multiple | Original code uses camelCase names, missing module/function documentation, `object` inheritance, and unidiomatic control flow. | Use snake_case names, docstrings, modern class syntax, clearer branches, and initialize all auction state. |
| Flake8 formatting findings | Style | Multiple | Original code has missing blank lines, long lines, and spacing/style violations. | Format the updated implementation to pass Flake8. |

## Final verification

- Pylint: **10.00/10**
- Bandit: **No issues identified**
- Flake8: **No findings**

The analyzer reports are saved as `pylint_before.txt`, `bandit_before.txt`,
`flake8_before.txt`, `pylint_report.txt`, `bandit_report.txt`, and
`flake8_report.txt`.
