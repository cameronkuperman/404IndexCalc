#!/usr/bin/env python3
"""Interactive runner for the existing IndexCalc implementation.

This does not change the index-calculus algorithm. It just gives us a safer
way to try arbitrary (p, g, y) inputs, time them, and verify g^x = y mod p.
Each trial runs in a child process so a hard example cannot freeze the runner.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass


SAMPLES = [
    (654323, 5, 168383),
    (8675309, 2, 7401598),
    (24687539, 2, 10448404),
    (9876543211, 12, 389221466),
    (246810135821, 2, 193839234994),
]


def missing_dependency_message(package: str) -> str:
    return (
        f"Missing dependency: {package}\n"
        "Run:\n"
        "  python3 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "  python3 -m pip install -r requirements.txt"
    )


def dependencies_available() -> bool:
    if importlib.util.find_spec("sympy") is None:
        print(missing_dependency_message("sympy"), file=sys.stderr)
        return False
    return True


CHILD_CODE = r"""
import importlib
import json
import random
import sys
import time

module_name, seed_text, p_text, g_text, y_text = sys.argv[1:]
p = int(p_text, 0)
g = int(g_text, 0)
y = int(y_text, 0)
seed = None if seed_text == "none" else int(seed_text)
if seed is not None:
    random.seed(seed)

start = time.perf_counter()
module = importlib.import_module(module_name)
ic = module.IndexCalc(p, g)
bound, factor_base = ic.computeFactorBase(p)
x = int(ic.indexCalcAlgoFull(p, g, y))
elapsed = time.perf_counter() - start

print(json.dumps({
    "p": p,
    "g": g,
    "y": y,
    "x": x,
    "verified": pow(g, x, p) == y % p,
    "seconds": elapsed,
    "factor_base_bound": int(bound),
    "factor_base_size": len(list(factor_base)),
}))
"""


@dataclass(frozen=True)
class Trial:
    p: int
    g: int
    y: int


def parse_int(text: str) -> int:
    return int(text.replace(",", "").replace("_", ""), 0)


def parse_trial(parts: list[str]) -> Trial:
    if len(parts) != 3:
        raise ValueError("expected exactly three values: p g y")
    return Trial(*(parse_int(part) for part in parts))


def parse_line(line: str) -> Trial:
    cleaned = line.replace(",", " ")
    return parse_trial(shlex.split(cleaned))


def run_trial(trial: Trial, module: str, timeout: float, seed: int | None) -> dict[str, object]:
    command = [
        sys.executable,
        "-B",
        "-c",
        CHILD_CODE,
        module,
        "none" if seed is None else str(seed),
        str(trial.p),
        str(trial.g),
        str(trial.y),
    ]

    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "p": trial.p,
            "g": trial.g,
            "y": trial.y,
            "timeout": timeout,
        }

    if result.returncode != 0:
        return {
            "p": trial.p,
            "g": trial.g,
            "y": trial.y,
            "error": result.stderr.strip() or result.stdout.strip(),
        }

    return json.loads(result.stdout)


def print_result(result: dict[str, object]) -> None:
    p = result["p"]
    g = result["g"]
    y = result["y"]

    if "timeout" in result:
        print(f"p={p}, g={g}, y={y} -> TIMEOUT after {result['timeout']}s", flush=True)
        return

    if "error" in result:
        print(f"p={p}, g={g}, y={y} -> ERROR", flush=True)
        print(result["error"], flush=True)
        return

    print(
        f"p={p}, g={g}, y={y} -> x={result['x']} "
        f"verified={result['verified']} time={float(result['seconds']):.3f}s "
        f"B={result['factor_base_bound']} base_size={result['factor_base_size']}",
        flush=True,
    )


def interactive(module: str, timeout: float, seed: int | None) -> None:
    print("Index calculus runner")
    print("Type: p g y")
    print("Examples: 23 5 18   or   654323 5 168383")
    print("Commands: samples, quit")

    while True:
        try:
            line = input("index-calc> ").strip()
        except EOFError:
            print()
            return

        if not line:
            continue
        if line.lower() in {"q", "quit", "exit"}:
            return
        if line.lower() == "samples":
            for p, g, y in SAMPLES:
                print_result(run_trial(Trial(p, g, y), module, timeout, seed))
            continue

        try:
            trial = parse_line(line)
        except ValueError as exc:
            print(f"Bad input: {exc}")
            continue

        print_result(run_trial(trial, module, timeout, seed))


def trials_from_stdin() -> list[Trial]:
    trials: list[Trial] = []
    for line_number, line in enumerate(sys.stdin, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            trials.append(parse_line(line))
        except ValueError as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    return trials


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run arbitrary discrete-log trials through your IndexCalc class.",
    )
    parser.add_argument("values", nargs="*", help="one trial as: p g y")
    parser.add_argument("--samples", action="store_true", help="run the professor sample inputs")
    parser.add_argument("--stdin", action="store_true", help="read one p g y triple per line")
    parser.add_argument("--timeout", type=float, default=15.0, help="seconds before a trial is stopped")
    parser.add_argument("--seed", type=int, default=404, help="random seed for repeatable runs")
    parser.add_argument("--no-seed", action="store_true", help="do not seed randomness")
    parser.add_argument(
        "--module",
        choices=["index_calc_optimized", "simplifiedIC"],
        default="index_calc_optimized",
        help="which existing implementation file to run",
    )
    args = parser.parse_args()

    if not dependencies_available():
        return 1

    seed = None if args.no_seed else args.seed

    try:
        if args.values:
            trials = [parse_trial(args.values)]
        elif args.samples:
            trials = [Trial(*sample) for sample in SAMPLES]
        elif args.stdin:
            trials = trials_from_stdin()
        else:
            interactive(args.module, args.timeout, seed)
            return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for trial in trials:
        print_result(run_trial(trial, args.module, args.timeout, seed))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        raise SystemExit(130)
