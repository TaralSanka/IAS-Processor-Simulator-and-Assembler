"""End-to-end checks: assemble a program, then run it on the simulator.

Runs under pytest, or directly with ``python tests/test_toolchain.py``.
"""

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ias import isa                                  # noqa: E402
from ias.assembler import AssemblyError, assemble    # noqa: E402
from ias.processor import Processor, load_image      # noqa: E402

PROGRAMS = os.path.join(ROOT, "programs")
SUBMISSION = os.path.join(ROOT, "submission")

N_ADDRESS = 0       # M(0) holds n
RESULT_ADDRESS = 7  # M(7) holds n!


def read(path):
    with open(path) as handle:
        return handle.read()


def assemble_factorial(n=None):
    """Assemble factorial.asm, optionally overriding the value of n."""
    source = read(os.path.join(PROGRAMS, "factorial.asm"))
    if n is not None:
        source = source.replace("\n5  ", "\n%d  " % n, 1)
    return assemble(source)


def run(words):
    cpu = Processor(words)
    cpu.run()
    return cpu


# -- assembler -----------------------------------------------------------

def test_every_word_is_40_bits():
    for word in assemble_factorial():
        assert len(word) == isa.WORD_BITS
        assert set(word) <= set("01")


def test_halves_are_opcode_plus_address():
    """Each half is an 8-bit opcode from the table plus a 12-bit address."""
    for word in assemble_factorial()[1:-1]:  # skip the two data words
        for half in (word[:isa.HALF_BITS], word[isa.HALF_BITS:]):
            opcode, address = half[:isa.OPCODE_BITS], half[isa.OPCODE_BITS:]
            assert opcode in isa.BY_OPCODE, opcode
            assert len(address) == isa.ADDRESS_BITS


def test_matches_original_submitted_machine_code():
    """The rewritten assembler reproduces the machine code that was submitted."""
    original = read(os.path.join(SUBMISSION, "binaryCode.txt")).split()
    assert assemble_factorial() == original


def test_committed_binary_is_up_to_date():
    committed = read(os.path.join(PROGRAMS, "factorial.bin.txt")).split()
    assert assemble_factorial() == committed


def test_rejects_unknown_instruction():
    try:
        assemble("FLY M(3)")
    except AssemblyError as error:
        assert "unknown instruction" in str(error)
    else:
        raise AssertionError("expected an AssemblyError")


def test_rejects_missing_address():
    try:
        assemble("LOAD M()")
    except AssemblyError as error:
        assert "needs an address" in str(error)
    else:
        raise AssertionError("expected an AssemblyError")


# -- simulator -----------------------------------------------------------

def test_factorial_of_five():
    cpu = run(assemble_factorial())
    assert cpu.word(RESULT_ADDRESS) == 120


def test_factorial_over_a_range():
    for n in range(0, 8):
        cpu = run(assemble_factorial(n))
        assert cpu.word(RESULT_ADDRESS) == math.factorial(n), "%d! wrong" % n


def test_zero_skips_the_loop_entirely():
    """COMPARE/JUMP+ must branch past the loop when n is already 0."""
    cpu = run(assemble_factorial(0))
    assert cpu.word(RESULT_ADDRESS) == 1
    assert cpu.cycles == 2  # the COMPARE word, then the HALT word


def test_counter_is_consumed():
    cpu = run(assemble_factorial())
    assert cpu.word(N_ADDRESS) == 0


def test_runs_the_original_submitted_binary():
    cpu = run(load_image(os.path.join(SUBMISSION, "binaryCode.txt")))
    assert cpu.word(RESULT_ADDRESS) == 120


def test_undefined_opcode_is_rejected():
    padding = "0" * isa.WORD_BITS   # M(0) is data; execution starts at M(1)
    bad = "01010101" + "0" * 32
    try:
        run([padding, bad])
    except ValueError as error:
        assert "undefined opcode" in str(error)
    else:
        raise AssertionError("expected a ValueError")


def test_running_off_the_end_of_memory_is_reported():
    """A program with no HALT must fail with a diagnosis, not an IndexError."""
    nops = ["0" * isa.WORD_BITS] * 4
    try:
        run(nops)
    except ValueError as error:
        assert "outside memory" in str(error)
    else:
        raise AssertionError("expected a ValueError")


# -- bit helpers ---------------------------------------------------------

def test_two_s_complement_round_trip():
    for value in (0, 1, 120, -1, -120, 2 ** 39 - 1, -(2 ** 39)):
        bits = isa.to_bits(value, isa.WORD_BITS)
        assert len(bits) == isa.WORD_BITS
        assert isa.from_bits(bits, signed=True) == value


if __name__ == "__main__":
    tests = sorted(
        (name, function)
        for name, function in globals().items()
        if name.startswith("test_") and callable(function)
    )
    for name, function in tests:
        function()
        print("ok   %s" % name)
    print("\n%d tests passed" % len(tests))
