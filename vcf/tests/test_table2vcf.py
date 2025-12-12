from __future__ import annotations

from pathlib import Path

import pytest
import typer

from vcf.table2vcf import parse_and_convert


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_missing_required_columns_raises(tmp_path: Path) -> None:
    input_path = tmp_path / "in.tsv"
    output_path = tmp_path / "out.vcf"

    _write_text(
        input_path,
        "chrom\tpos\trefer\nchr1\t1\tA\n",
    )

    with pytest.raises(typer.Exit):
        parse_and_convert(input_file=input_path, output_file=output_path)


def test_header_normalization_case_whitespace(tmp_path: Path) -> None:
    input_path = tmp_path / "in.tsv"
    output_path = tmp_path / "out.vcf"

    _write_text(
        input_path,
        " Chrom \t POS\t Refer\tALT \nchr1\t1\tA\tT\n",
    )

    parse_and_convert(input_file=input_path, output_file=output_path, chunksize=1)

    lines = _read_lines(output_path)
    assert lines[0].startswith("##fileformat=VCFv4.2")
    assert lines[5].startswith("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")
    assert lines[6].split("\t")[:5] == ["chr1", "1", ".", "A", "T"]


def test_convert_skips_invalid_pos_and_writes_variants(tmp_path: Path) -> None:
    input_path = tmp_path / "in.tsv"
    output_path = tmp_path / "out.vcf"

    _write_text(
        input_path,
        "chrom\tpos\trefer\talt\nchr1\t1\tA\tT\nchr1\tabc\tC\tG\n chr2 \t 2 \t G \t A \n",
    )

    parse_and_convert(input_file=input_path, output_file=output_path, chunksize=2)

    lines = _read_lines(output_path)

    # 6 header lines + 2 variant lines (invalid POS dropped)
    assert len(lines) == 8

    variant1 = lines[6].split("\t")
    variant2 = lines[7].split("\t")

    assert variant1 == ["chr1", "1", ".", "A", "T", ".", ".", "."]
    assert variant2 == ["chr2", "2", ".", "G", "A", ".", ".", "."]


def test_chunksize_one_processes_multiple_chunks(tmp_path: Path) -> None:
    input_path = tmp_path / "in.tsv"
    output_path = tmp_path / "out.vcf"

    _write_text(
        input_path,
        "chrom\tpos\trefer\talt\nchr1\t1\tA\tT\nchr1\t2\tC\tG\nchr2\t3\tG\tA\n",
    )

    parse_and_convert(input_file=input_path, output_file=output_path, chunksize=1)

    lines = _read_lines(output_path)
    assert len(lines) == 9  # 6 header + 3 variants
    assert lines[6].split("\t")[:5] == ["chr1", "1", ".", "A", "T"]
    assert lines[7].split("\t")[:5] == ["chr1", "2", ".", "C", "G"]
    assert lines[8].split("\t")[:5] == ["chr2", "3", ".", "G", "A"]
