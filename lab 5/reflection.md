# Reflection

## 1. What is static code analysis, and how does it help?

Static code analysis checks source code without running the application. It
helps find likely defects, unsafe coding patterns, and style problems early,
before those issues reach users. It also gives a repeatable way to review code
quality.

## 2. Which tools were used, and what did each contribute?

Pylint reviewed Python code quality and design conventions. Bandit searched for
common security risks, including unsafe XML-RPC parsing. Flake8 checked style
and formatting. Using all three gave complementary feedback rather than relying
on one tool's scope.

## 3. Which issues were most important, and how were they fixed?

The highest-risk issues were HTML injection in listings and badges and the
unsafe XML-RPC parser flagged by Bandit. I enabled template autoescaping,
escaped bidder names, and applied `defusedxml`'s XML-RPC patch. I also fixed
auction logic that accepted seller bids, ignored the reserve and minimum
increment, mishandled time comparisons, and hid unrelated errors with a broad
exception handler.

## 4. What did you learn, and what challenges did you encounter?

The tools catch different classes of problems, and a clean report does not
replace checking whether the program behaves correctly. The demo exposed
functional auction bugs that were not all analyzer findings. One challenge was
distinguishing a security mitigation from a suppressed warning: the final
Bandit report has no findings, and the targeted B411 suppression is documented
next to the import that is hardened by `defusedxml`.
