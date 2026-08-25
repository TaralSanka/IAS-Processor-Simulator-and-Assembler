# Original submission (Feb 2024)

These are the files as handed in for EG 212 Assignment 1, content unmodified;
the working code lives in [`../ias/`](../ias/), and the report submitted with
them is [`../docs/report.pdf`](../docs/report.pdf).

The assignment brief required each filename to be prefixed with the
submitter's roll number (`IMT2023588_`) for the LMS upload. That prefix has
been dropped here since it carries no meaning outside that submission; the
file contents are exactly as submitted.

| File | |
|---|---|
| `assembly.txt` | the IAS assembly program |
| `binaryCode.txt` | the machine code that was submitted |
| `processor.py` | the simulator |
| `assembler.py` | the assembler |
| `factorialCcode.c` | the C file submitted with it |

Two things to know before reading them, both discussed in the top-level
README:

- `assembler.py` does **not** produce `binaryCode.txt`. It holds the assembly
  as a hardcoded Python list instead of reading the `.txt` file, and its
  operand handling puts the addresses on the wrong instructions. The binary
  that was submitted is correct; the assembler that was submitted does not
  generate it.
- `factorialCcode.c` is a primality test, not a factorial — the wrong C file
  went into the archive. The assembly is a factorial.

`processor.py` does run, and prints 120 for 5!. It expects a file named
`binaryCode.txt` in the working directory, which is already its name here:

```bash
python processor.py
```

The rewritten assembler in `../ias/` reproduces `binaryCode.txt` byte for
byte, and the rewritten simulator runs it to the same result; both are
asserted by the test suite.
