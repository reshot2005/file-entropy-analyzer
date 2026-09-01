# File Entropy Analyzer

A lightweight, dependency-free Python utility that calculates the **Shannon entropy** of a file's byte distribution.

Entropy analysis is useful in defensive file triage because unusually high entropy can be consistent with encrypted, compressed, or packed data, while low entropy can be consistent with plain text or repetitive content.

> **Important:** Entropy is an indicator, not proof of encryption, compression, malware packing, or any other specific file property.

## Features

- Shannon entropy calculation in bits per byte
- Streaming file processing
- Does not load the entire file into memory
- Configurable chunk size
- Human-readable output
- JSON output for automation
- Conservative interpretation thresholds
- Handles empty files
- Clear error handling
- Unit tests
- GitHub Actions CI
- Python 3.10–3.14
- Zero third-party dependencies

## Requirements

- Python 3.10+
- Read access to the target file

No third-party Python packages are required.

## Usage

Analyze a file:

```bash
python3 entropy_analyzer.py --file suspicious.bin
```

JSON output:

```bash
python3 entropy_analyzer.py \
  --file suspicious.bin \
  --format json
```

Use a smaller or larger processing chunk:

```bash
python3 entropy_analyzer.py \
  --file suspicious.bin \
  --chunk-size 262144
```

## Example output

```text
File: suspicious.bin
File size: 1,048,576 bytes
Shannon entropy: 7.842 bits/byte (maximum 8.0)
Assessment: High entropy; consistent with compressed, encrypted, or packed data.
```

## How it works

For a byte distribution with probabilities `p(x)`, Shannon entropy is:

```text
H(X) = -Σ p(x) log2(p(x))
```

For arbitrary bytes, the theoretical maximum is **8 bits per byte**, which occurs when all 256 possible byte values are equally represented.

The tool counts byte frequencies while streaming the file and then calculates the entropy from those frequencies.

## Interpretation

The default thresholds are:

| Entropy | Interpretation |
|---:|---|
| `< 3.0` | Low entropy |
| `3.0–7.5` | Moderate entropy |
| `> 7.5` | High entropy |

These thresholds are intentionally only heuristic.

### High entropy does not mean "encrypted"

High entropy can occur in:

- encrypted data
- compressed archives
- compressed media
- packed executables
- generated binary data
- random data
- some filesystem/database structures

Likewise, malware or encrypted material can sometimes contain low-entropy regions.

For malware triage or forensic analysis, combine entropy with other indicators such as file type, headers/magic bytes, metadata, structure, strings, signatures, and behavioral evidence.

## Limitations

This tool:

- analyzes the complete byte distribution
- does not perform sliding-window entropy analysis
- does not identify file types
- does not detect encryption directly
- does not unpack archives
- does not inspect executable behavior
- does not modify the analyzed file

Because the calculation is global, a file containing both low- and high-entropy regions can receive a middle-range overall score.

## Security and privacy

The tool reads the target file but does not modify it or transmit its contents.

The JSON output includes the analyzed path. Review generated reports before sharing them externally because paths can contain usernames, project names, or other environment-specific information.

Use it only on files and systems you are authorized to inspect.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Analysis completed successfully |
| `1` | File could not be read |
| `2` | Invalid input or target path |

## Development

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## License

MIT. See [LICENSE](LICENSE).
