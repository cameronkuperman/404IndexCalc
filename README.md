# Math 404 Index Calculus

## Setup

From a fresh clone, make a virtual environment and install the one Python
dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

After that, run commands from the same activated environment. Your shell prompt
should usually show `(.venv)`.

## Run A Test

```bash
python3 -B race_index_calc.py 23 5 18
```

Interactive mode:

```bash
python3 -B race_index_calc.py
```

Then enter triples as:

```text
p g y
```

For example:

```text
23 5 18
```

Run the assignment samples with a timeout:

```bash
python3 -B race_index_calc.py --samples --timeout 30
```

The runner calls the existing `IndexCalc` implementation and verifies whether
`g^x = y mod p`.
