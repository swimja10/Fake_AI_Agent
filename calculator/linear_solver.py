"""
Solve simple linear equations in one variable, e.g. "5 + 4x = 9" -> x = 1.

Supports:
  - numbers (integers and decimals), + - * / and parentheses
  - implicit multiplication like "4x", "2(x + 1)", "3(2 - x)"
  - the variable on either side of the equals sign

Uses exact fractions internally, so results are not affected by floating-point error.
"""

import re
from fractions import Fraction

_TOKEN_RE = re.compile(r"\d+\.?\d*|\.\d+|[A-Za-z]+|[-+*/()=]")


def _tokenize(text, variable):
    cleaned = text.replace(" ", "")
    raw = _TOKEN_RE.findall(cleaned)
    if "".join(raw) != cleaned:
        raise ValueError(f"Invalid characters in equation: {text!r}")

    tokens = []
    for tok in raw:
        if tok[0].isalpha() and tok != variable:
            raise ValueError(f"Unknown variable {tok!r} (expected {variable!r})")
        # Insert implicit '*' such as "4x", "2(x+1)", "x(3)", ")(".
        if tokens:
            prev = tokens[-1]
            prev_ends_operand = (
                prev == ")" or prev == variable or prev[0].isdigit() or prev[0] == "."
            )
            starts_operand = (
                tok == "(" or tok == variable or tok[0].isdigit() or tok[0] == "."
            )
            if prev_ends_operand and starts_operand:
                tokens.append("*")
        tokens.append(tok)
    return tokens


class _Parser:
    """Recursive-descent parser. Each expression is reduced to a pair (a, b)
    meaning the linear expression a*x + b."""

    def __init__(self, tokens, variable):
        self.tokens = tokens
        self.pos = 0
        self.variable = variable

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def parse(self):
        result = self._parse_expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token {self._peek()!r}")
        return result

    def _parse_expr(self):
        left = self._parse_term()
        while self._peek() in ("+", "-"):
            op = self._next()
            right = self._parse_term()
            if op == "+":
                left = (left[0] + right[0], left[1] + right[1])
            else:
                left = (left[0] - right[0], left[1] - right[1])
        return left

    def _parse_term(self):
        left = self._parse_factor()
        while self._peek() in ("*", "/"):
            op = self._next()
            right = self._parse_factor()
            if op == "*":
                if left[0] != 0 and right[0] != 0:
                    raise ValueError(
                        "Nonlinear equation: variable multiplied by itself"
                    )
                left = (left[0] * right[1] + right[0] * left[1], left[1] * right[1])
            else:
                if right[0] != 0:
                    raise ValueError("Nonlinear equation: division by the variable")
                if right[1] == 0:
                    raise ValueError("Division by zero")
                left = (left[0] / right[1], left[1] / right[1])
        return left

    def _parse_factor(self):
        tok = self._next()
        if tok is None:
            raise ValueError("Unexpected end of equation")
        if tok == "-":
            a, b = self._parse_factor()
            return (-a, -b)
        if tok == "+":
            return self._parse_factor()
        if tok == "(":
            inner = self._parse_expr()
            if self._next() != ")":
                raise ValueError("Missing closing parenthesis")
            return inner
        if tok == self.variable:
            return (Fraction(1), Fraction(0))
        try:
            return (Fraction(0), Fraction(tok))
        except (ValueError, ZeroDivisionError):
            raise ValueError(f"Unexpected token {tok!r}") from None


def _parse_side(text, variable):
    tokens = _tokenize(text, variable)
    if not tokens:
        raise ValueError("Empty side in equation")
    return _Parser(tokens, variable).parse()


def solve_linear(equation, variable="x"):
    """
    Solve a linear equation in one variable.

    >>> solve_linear("5+4x=9")
    Fraction(1, 1)
    >>> solve_linear("2(x+1) = 3x - 4")
    Fraction(6, 1)

    Returns a Fraction. Raises ValueError if the equation is not linear,
    has no solution, or has infinitely many solutions.
    """
    if equation.count("=") != 1:
        raise ValueError("Equation must contain exactly one '='")

    left_text, right_text = equation.split("=")
    left = _parse_side(left_text, variable)
    right = _parse_side(right_text, variable)

    # Move everything to one side: A*x + B = 0
    A = left[0] - right[0]
    B = left[1] - right[1]

    if A == 0:
        if B == 0:
            raise ValueError("Infinitely many solutions (equation is always true)")
        raise ValueError("No solution (equation is never true)")

    return -B / A


if __name__ == "__main__":
    examples = [
        "5+4x=9",
        "2x - 7 = 3",
        "x/2 + 3 = 10",
        "3(x - 2) = 2x + 1",
        "7 = 2x + 1",
        "2(x+1) = 2x + 2",
        "x + 1 = x + 2",
        "0.5x = 2",
    ]
    for eq in examples:
        try:
            print(f"{eq:<20} -> x = {solve_linear(eq)}")
        except ValueError as e:
            print(f"{eq:<20} -> error: {e}")
