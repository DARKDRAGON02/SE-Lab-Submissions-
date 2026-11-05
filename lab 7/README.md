# Lab 7: Fuzzing for Input Validation Bugs

Kishan S, PES2UG23CS277, Software Engineering Lab (5th semester).

The module `bowling_alley_parser.py` reads bowling alley details from the console. It used to assume that every input was well formed, so `None`, an empty string or a bad frame made it crash. I completed the three Hypothesis tests in `test_bowling_alley_parser.py`, ran them against the old module, and then fixed the module until the same tests passed.

## Files

- `bowling_alley_parser.py`: the fixed module. Every function checks the type, the length and the characters before it does any work.
- `test_bowling_alley_parser.py`: three Hypothesis tests, one per function. Each test checks that the call does not raise and that the return type is right.
- `PES2UG23CS277_KISHAN_S_LAB7.pdf`: the report with the four screenshots and the reflection answers.
- `report.tex`: the LaTeX source of the report.
- `screenshots/`: the four terminal shots used in the report.

## How to run

```
pip install hypothesis pytest
python bowling_alley_parser.py
python -m pytest test_bowling_alley_parser.py -v
```

## Results

On the buggy module the tests fail with `3 failed`. On the fixed module they pass with `3 passed`. The inputs that Hypothesis shrank to were `None`, an empty string, `0`, `:` and `0:`. Table 1 in the report lists all of them with the errors.
