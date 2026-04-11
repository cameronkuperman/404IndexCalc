from simplifiedIC import IndexCalc


def main():
    ic = IndexCalc(101, 2)
    base_list = [2, 3, 5, 7, 11]

    samples = [12, 18, 72, 98]

    for num in samples:
        print(f"n={num}")
        print("factorization:", ic.factor(num))
        print("log vector:", ic.createLogVector(num, base_list))
        print()


if __name__ == "__main__":
    main()
