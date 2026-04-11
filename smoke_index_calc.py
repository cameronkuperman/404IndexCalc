from simplifiedIC import IndexCalc


def brute_force_log(g, target, p):
    for x in range(1, p):
        if pow(g, x, p) == target:
            return x
    return None


def main():
    p = 23
    g = 5
    target = 18

    ic = IndexCalc(p, g)
    b, factor_base = ic.computeFactorBase(p)

    print(f"p={p}, g={g}, target={target}")
    print("factor base bound:", b)
    print("factor base:", list(factor_base))
    print("target factorization:", ic.factor(target))
    print("target vector:", ic.createLogVector(target, factor_base))
    print("expected x from brute force:", brute_force_log(g, target, p))

    try:
        print("solveForX:", ic.solveForX(target, p))
    except Exception as exc:
        print("solveForX raised:", repr(exc))


if __name__ == "__main__":
    main()
