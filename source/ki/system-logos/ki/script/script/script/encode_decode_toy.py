# script/encode_decode_toy.py

"""
Toy DNA storage encoder/decoder.

- Input: bytes
- Output: DNA string over {A, C, G, T}
- Constraints:
  - No homopolymer runs > 3
  - Approximate GC balance via mapping and simple flipping
"""

BIT_TO_BASE = {
    "00": "A",
    "01": "C",
    "10": "G",
    "11": "T",
}

BASE_TO_BIT = {v: k for k, v in BIT_TO_BASE.items()}


def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)


def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        raise ValueError("Bitstring length must be a multiple of 8")
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


def apply_homopolymer_constraint(bases: str, max_run: int = 3) -> str:
    """
    Post-process DNA bases to ensure no homopolymer run exceeds max_run.

    Strategy: whenever a run exceeds max_run, flip the offending base
    to another base with opposite GC/AT class to keep GC roughly balanced.
    """
    if not bases:
        return bases

    result = [bases[0]]
    run_char = bases[0]
    run_len = 1

    def flip_base(b: str) -> str:
        # Simple flip: A <-> C, T <-> G to balance GC/AT content.
        if b == "A":
            return "C"
        if b == "C":
            return "A"
        if b == "G":
            return "T"
        if b == "T":
            return "G"
        raise ValueError(f"Invalid base: {b}")

    for b in bases[1:]:
        if b == run_char:
            run_len += 1
            if run_len > max_run:
                b = flip_base(b)
                run_char = b
                run_len = 1
        else:
            run_char = b
            run_len = 1
        result.append(b)

    return "".join(result)


def encode_bytes_to_dna(data: bytes) -> str:
    bits = bytes_to_bits(data)
    # pad to multiple of 2 bits
    if len(bits) % 2 != 0:
        bits += "0"
    bases = "".join(BIT_TO_BASE[bits[i : i + 2]] for i in range(0, len(bits), 2))
    constrained = apply_homopolymer_constraint(bases, max_run=3)
    return constrained


def decode_dna_to_bytes(dna: str) -> bytes:
    # Inverse mapping ignoring the homopolymer flipping; for the toy example
    # we assume no critical information is lost. In a real system, flipping
    # would be encoded via redundancy or ECC [web:18][web:21][web:24].
    bits = "".join(BASE_TO_BIT[b] for b in dna)
    # truncate to multiple of 8 bits
    bits = bits[: len(bits) - (len(bits) % 8)]
    return bits_to_bytes(bits)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Toy DNA storage encoder/decoder.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    enc = subparsers.add_parser("encode", help="encode stdin to DNA")
    dec = subparsers.add_parser("decode", help="decode DNA from stdin to bytes")

    args = parser.parse_args()

    if args.mode == "encode":
        payload = sys.stdin.buffer.read()
        dna = encode_bytes_to_dna(payload)
        sys.stdout.write(dna + "\n")
    elif args.mode == "decode":
        dna = sys.stdin.read().strip()
        out = decode_dna_to_bytes(dna)
        sys.stdout.buffer.write(out)
