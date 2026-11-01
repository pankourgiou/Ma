#!/usr/bin/env python3
"""Builds an ~800 MB HTML file of math operations. Standard library only (no numpy).
Every row is verified 20 different ways before it is written.

Usage:  python make_math_800MB.py            (800 MB)
        python make_math_800MB.py 50         (custom size in MB, e.g. a quick test)
"""
import sys, time, random
from math import gcd, lcm, isqrt
from fractions import Fraction
from decimal import Decimal

SIZE_MB = int(sys.argv[1]) if len(sys.argv) > 1 else 800
TARGET = SIZE_MB * 1_000_000
OUT = f"math_operations_{SIZE_MB}MB.html"
BATCH = 50_000
rnd = random.Random(2026)


def row(i):
    a = rnd.randrange(1, 1_000_000_000)
    b = rnd.randrange(1, 1_000_000_000)
    s, d, p = a + b, a - b, a * b
    q, r = divmod(a, b)
    g = gcd(a, b)
    rt = isqrt(a)
    checks = (
        s == sum((a, b)),                              # 1  recompute sum
        s - b == a,                                    # 2  inverse of sum
        d + b == a,                                    # 3  inverse of difference
        p // a == b,                                   # 4  inverse of product
        q * b + r == a,                                # 5  division identity
        0 <= r < b,                                    # 6  remainder range
        a % g == 0 and b % g == 0,                     # 7  gcd divides both
        gcd(a // g, b // g) == 1,                      # 8  reduced pair is coprime
        lcm(a, b) * g == p,                            # 9  lcm * gcd = product
        rt * rt <= a < (rt + 1) ** 2,                  # 10 integer square root bounds
        s % 9 == (a % 9 + b % 9) % 9,                  # 11 casting out nines (sum)
        p % 9 == (a % 9) * (b % 9) % 9,                # 12 casting out nines (product)
        p % 7 == (a % 7) * (b % 7) % 7,                # 13 mod 7 product
        p % 11 == (a % 11) * (b % 11) % 11,            # 14 mod 11 product
        s & 1 == (a ^ b) & 1,                          # 15 parity of sum
        (a ^ b) + 2 * (a & b) == s,                    # 16 xor/and identity
        s * s - d * d == 4 * p,                        # 17 (a+b)^2-(a-b)^2 = 4ab
        pow(a, 2, 1_000_003) * pow(b, 2, 1_000_003) % 1_000_003
        == pow(p, 2, 1_000_003),                       # 18 modular power
        Fraction(a, b) * b == a,                       # 19 exact rational check
        Decimal(a) * Decimal(b) == p,                  # 20 decimal check
    )
    if not all(checks):
        raise SystemExit(f"CHECK FAILED on row {i}: a={a} b={b}")
    return f"<tr><td>{i}<td>{a}<td>{b}<td>{s}<td>{d}<td>{p}<td>{q}<td>{r}<td>{g}<td>{rt}\n"


# ---- quick benchmark for the time estimate ----
t0 = time.perf_counter()
sample = "".join(row(i) for i in range(20_000))
per_row_t = (time.perf_counter() - t0) / 20_000
per_row_b = len(sample.encode()) / 20_000
est_rows = int(TARGET / per_row_b)
est_min = per_row_t * est_rows / 60
print(f"Estimated rows: {est_rows:,}  |  estimated time: {est_min:.1f} min", flush=True)

head = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Math Operations - {SIZE_MB} MB</title>
<style>body{{font-family:system-ui,sans-serif;margin:1rem}}table{{border-collapse:collapse;font:12px monospace}}
td,th{{border:1px solid #8884;padding:2px 6px;text-align:right}}</style></head><body>
<h1>Math operations dataset (~{SIZE_MB} MB)</h1>
<p>About {est_rows:,} rows. Columns: a+b, a-b, a*b, a div b, a mod b, gcd(a,b), isqrt(a).</p>
<p><b>Verification:</b> every row passed 20 independent checks (inverse operations, division identity,
gcd/lcm relations, integer square-root bounds, mod 7/9/11 tests, bitwise and algebraic identities,
modular powers, exact Fraction check, Decimal check).</p>
<p><b>Estimated generation time on this machine:</b> about {est_min:.1f} minutes.</p>
<p><b>Warning:</b> browsers will freeze on a file this size. Use a large-file text editor, <code>less</code> or <code>grep</code>.</p>
<table><thead><tr><th>#<th>a<th>b<th>a+b<th>a-b<th>a*b<th>a div b<th>a mod b<th>gcd<th>isqrt(a)</thead><tbody>
"""

start = time.perf_counter()
written, i = 0, 0
with open(OUT, "w", encoding="ascii", newline="\n") as f:
    f.write(head); written += len(head)
    while written < TARGET - 500:
        n = min(BATCH, max(1, (TARGET - 500 - written) // int(per_row_b + 1)))
        chunk = "".join(row(i + k) for k in range(n))
        f.write(chunk); written += len(chunk); i += n
        print(f"\r{written/1e6:7.1f} MB / {SIZE_MB} MB   {time.perf_counter()-start:6.0f}s", end="", flush=True)
    elapsed = time.perf_counter() - start
    f.write(f"</tbody></table>\n<p><b>Done.</b> {i:,} rows, 20/20 checks passed on every row. "
            f"Actual time: {elapsed/60:.1f} min.</p>\n</body></html>\n")
print(f"\nDone: {OUT}, {i:,} rows, {elapsed/60:.1f} min")
