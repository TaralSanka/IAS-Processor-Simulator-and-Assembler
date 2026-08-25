"""Assembler for the IAS assembly dialect used in this project.

Source format
-------------
One line of source produces one 40-bit memory word.

* A line holding a single integer is a **data word** and is emitted as a
  40-bit two's-complement constant.
* Any other line is an **instruction word** holding a left and a right
  half-instruction separated by two or more spaces (or a tab).  A line
  with only one instruction gets NOP in the right half.
* ``;`` starts a comment; blank lines are ignored.

Each half-instruction is packed as an 8-bit opcode followed by a 12-bit
address, giving the 20-bit halves that make up the word.
"""

import argparse
import re
import sys

from . import isa

COMMENT = ";"
#: Two or more spaces, or a tab, separate the two half-instructions.
HALF_SEPARATOR = re.compile(r"\s{2,}|\t")
#: First run of digits inside the operand is the address, e.g. M(6,0:19) -> 6.
ADDRESS = re.compile(r"\((\d+)")


class AssemblyError(Exception):
    """Raised for a source line the assembler cannot encode."""


def strip_comment(line):
    return line.split(COMMENT, 1)[0].rstrip()


def assemble_half(text):
    """Encode one half-instruction as a 20-bit string."""
    mnemonic = isa.normalise(text)
    instruction = isa.BY_MNEMONIC.get(mnemonic)
    if instruction is None:
        raise AssemblyError("unknown instruction %r" % text.strip())

    if not instruction.has_address:
        address = 0
    else:
        match = ADDRESS.search(text)
        if match is None:
            raise AssemblyError("%r needs an address operand" % text.strip())
        address = int(match.group(1))
        if not 0 <= address < (1 << isa.ADDRESS_BITS):
            raise AssemblyError("address %d out of range" % address)

    return instruction.opcode + isa.to_bits(address, isa.ADDRESS_BITS)


def assemble_line(line):
    """Encode one source line as a 40-bit string."""
    text = strip_comment(line)
    if not text.strip():
        return None

    try:
        return isa.to_bits(int(text.strip()), isa.WORD_BITS)
    except ValueError:
        pass  # not a bare integer, so it is an instruction word

    halves = [h for h in HALF_SEPARATOR.split(text.strip()) if h.strip()]
    if len(halves) == 1:
        halves.append(isa.NOP.mnemonic)
    if len(halves) != 2:
        raise AssemblyError("expected at most two instructions, got %d" % len(halves))

    return "".join(assemble_half(h) for h in halves)


def assemble(source):
    """Assemble a whole program into a list of 40-bit strings."""
    words = []
    for number, line in enumerate(source.splitlines(), start=1):
        try:
            word = assemble_line(line)
        except AssemblyError as error:
            raise AssemblyError("line %d: %s" % (number, error))
        if word is not None:
            words.append(word)
    return words


def main(argv=None):
    parser = argparse.ArgumentParser(description="Assemble IAS assembly into machine code.")
    parser.add_argument("source", help="assembly source file (.asm)")
    parser.add_argument("-o", "--output", help="write machine code here (default: stdout)")
    args = parser.parse_args(argv)

    with open(args.source) as handle:
        words = assemble(handle.read())

    text = "\n".join(words) + "\n"
    if args.output:
        with open(args.output, "w") as handle:
            handle.write(text)
        print("%s: %d words -> %s" % (args.source, len(words), args.output))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
