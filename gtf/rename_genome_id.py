#!/usr/bin/env python3
"""
Rename chromosome IDs in genome FASTA and GFF files.

Supports two modes:
- NGDC: Extracts OriSeqID from NGDC FASTA headers
- Custom: Uses user-provided ID mapping file

Usage:
    # NGDC genome with OriSeqID
    tc-rename-genome-id ngdc -f genome.fasta -o output.fasta [-g input.gff -og output.gff]
    
    # Custom ID mapping file
    tc-rename-genome-id custom -f genome.fasta -o output.fasta -m id_map.txt [-g input.gff -og output.gff]
"""

import re
import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated


def parse_fasta_header(header):
    """
    Parse FASTA header to extract ID and OriSeqID.

    Example header:
    >GWHGECT00000001.1      Chromosome 1A   Complete=T      Circular=F      OriSeqID=Chr1A  Len=600907804

    Returns:
        tuple: (old_id, new_id) or (None, None) if OriSeqID not found
    """
    # Extract the first field (ID)
    parts = header.strip().split()
    if not parts:
        return None, None

    old_id = parts[0].lstrip(">")

    # Extract OriSeqID
    match = re.search(r"OriSeqID=(\S+)", header)
    if match:
        new_id = match.group(1)
        return old_id, new_id

    return None, None


def build_id_mapping(fasta_file):
    """
    Build a mapping dictionary from FASTA file.

    Args:
        fasta_file: Path to input FASTA file

    Returns:
        dict: Mapping from old IDs to new IDs
    """
    id_map = {}

    with open(fasta_file) as f:
        for line in f:
            if line.startswith(">"):
                old_id, new_id = parse_fasta_header(line)
                if old_id and new_id:
                    id_map[old_id] = new_id

    return id_map


def load_id_mapping(map_file):
    """
    Load ID mapping from a tab-separated file.

    Args:
        map_file: Path to mapping file (format: old_id\\tnew_id)

    Returns:
        dict: Mapping from old IDs to new IDs
    """
    id_map = {}

    with open(map_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                print(
                    f"Warning: Skipping invalid line {line_num} in mapping file: {line}",
                    file=sys.stderr,
                )
                continue

            old_id, new_id = parts[0].strip(), parts[1].strip()
            if old_id and new_id:
                id_map[old_id] = new_id

    return id_map


def rename_fasta(input_fasta, output_fasta, id_map):
    """
    Rename chromosome IDs in FASTA file.

    Args:
        input_fasta: Path to input FASTA file
        output_fasta: Path to output FASTA file
        id_map: Dictionary mapping old IDs to new IDs
    """
    with open(input_fasta) as infile, open(output_fasta, "w") as outfile:
        for line in infile:
            if line.startswith(">"):
                # Try to extract the first field as the sequence ID
                parts = line.strip().split()
                if parts:
                    seq_id = parts[0].lstrip(">")
                    if seq_id in id_map:
                        # Write simplified header with just the new ID
                        outfile.write(f">{id_map[seq_id]}\n")
                    else:
                        # If no mapping, try parsing as NGDC format
                        old_id, new_id = parse_fasta_header(line)
                        if old_id and new_id and old_id in id_map:
                            outfile.write(f">{new_id}\n")
                        else:
                            # Keep original header if no mapping found
                            outfile.write(line)
                else:
                    # Keep original header if parsing fails
                    outfile.write(line)
            else:
                outfile.write(line)


def rename_gff(input_gff, output_gff, id_map):
    """
    Rename chromosome IDs in GFF file.

    Args:
        input_gff: Path to input GFF file
        output_gff: Path to output GFF file
        id_map: Dictionary mapping old IDs to new IDs
    """
    with open(input_gff) as infile, open(output_gff, "w") as outfile:
        for line in infile:
            # Skip comment lines
            if line.startswith("#"):
                outfile.write(line)
                continue

            # Skip empty lines
            if not line.strip():
                outfile.write(line)
                continue

            # Process GFF lines
            fields = line.split("\t")
            if len(fields) >= 1:
                chrom = fields[0]
                if chrom in id_map:
                    fields[0] = id_map[chrom]
                outfile.write("\t".join(fields))
            else:
                outfile.write(line)


def main():
    app()


app = typer.Typer(help="Rename chromosome IDs in genome FASTA and GFF files")


@app.command()
def ngdc(
    fasta: Annotated[Path, typer.Option("-f", "--fasta", help="Input FASTA file")],
    output: Annotated[Path, typer.Option("-o", "--output", help="Output FASTA file")],
    gff: Annotated[Optional[Path], typer.Option("-g", "--gff", help="Input GFF file (optional)")] = None,
    output_gff: Annotated[
        Optional[Path], typer.Option("-og", "--output-gff", help="Output GFF file (optional)")
    ] = None,
):
    """
    Rename chromosome IDs using NGDC OriSeqID from FASTA headers.
    
    This command extracts OriSeqID values from NGDC FASTA headers and uses them
    to rename chromosome IDs in both FASTA and GFF files.
    """
    # Check GFF arguments consistency
    if gff and not output_gff:
        typer.echo("Error: --output-gff is required when --gff is specified", err=True)
        raise typer.Exit(1)
    if output_gff and not gff:
        typer.echo("Error: --gff is required when --output-gff is specified", err=True)
        raise typer.Exit(1)

    # Build ID mapping from FASTA
    typer.echo(f"Building ID mapping from {fasta} (OriSeqID)...", err=True)
    id_map = build_id_mapping(fasta)
    typer.echo(f"Found {len(id_map)} chromosome mappings", err=True)

    for old_id, new_id in sorted(id_map.items()):
        typer.echo(f"  {old_id} -> {new_id}", err=True)

    # Rename FASTA
    typer.echo(f"Renaming FASTA file to {output}...", err=True)
    rename_fasta(fasta, output, id_map)

    # Rename GFF if specified
    if gff:
        typer.echo(f"Renaming GFF file to {output_gff}...", err=True)
        rename_gff(gff, output_gff, id_map)

    typer.echo("Done!", err=True)


@app.command()
def custom(
    fasta: Annotated[Path, typer.Option("-f", "--fasta", help="Input FASTA file")],
    output: Annotated[Path, typer.Option("-o", "--output", help="Output FASTA file")],
    id_map: Annotated[Path, typer.Option("-m", "--map", help="ID mapping file (tab-separated: old_id\\tnew_id)")],
    gff: Annotated[Optional[Path], typer.Option("-g", "--gff", help="Input GFF file (optional)")] = None,
    output_gff: Annotated[
        Optional[Path], typer.Option("-og", "--output-gff", help="Output GFF file (optional)")
    ] = None,
):
    """
    Rename chromosome IDs using a custom ID mapping file.
    
    The mapping file should be tab-separated with format: old_id\\tnew_id
    Lines starting with # are treated as comments and empty lines are ignored.
    """
    # Check GFF arguments consistency
    if gff and not output_gff:
        typer.echo("Error: --output-gff is required when --gff is specified", err=True)
        raise typer.Exit(1)
    if output_gff and not gff:
        typer.echo("Error: --gff is required when --output-gff is specified", err=True)
        raise typer.Exit(1)

    # Load ID mapping from file
    typer.echo(f"Loading ID mapping from {id_map}...", err=True)
    mapping = load_id_mapping(id_map)
    typer.echo(f"Loaded {len(mapping)} chromosome mappings", err=True)

    for old_id, new_id in sorted(mapping.items()):
        typer.echo(f"  {old_id} -> {new_id}", err=True)

    # Rename FASTA
    typer.echo(f"Renaming FASTA file to {output}...", err=True)
    rename_fasta(fasta, output, mapping)

    # Rename GFF if specified
    if gff:
        typer.echo(f"Renaming GFF file to {output_gff}...", err=True)
        rename_gff(gff, output_gff, mapping)

    typer.echo("Done!", err=True)


if __name__ == "__main__":
    main()
