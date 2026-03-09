# Repository Guidelines

This file provides guidance to Codex when working with code in this repository.

## Project Overview

Divicast is a Chinese metaphysics(玄学) library that provides programmatic chart generation for various traditional divination systems.. Currently supports:
- **六爻 (Six-line divination)**: Core divination system
- **八字 (Eight-character birth chart)**: Natal chart analysis including fortune cycles, patterns (格局)

Goal: Provide all mainstream Chinese divination systems as a library, published to PyPI.

## Commands

```bash
# Install dependencies with uv
uv sync

# Run all tests
uv run python -m unittest

# Run a specific test file
uv run python -m unittest tests.test_geju

# Run examples
uv run python examples/sixline_example.py
uv run python examples/bazi_example.py
```


## Code Architecture

### Source Structure

```
src/divicast/
├── base/
│   └── symbol.py         # Base ValuedMultiton class for enum-like divination symbols
├── entities/             # Core data models and logic for all divination systems
│   ├── tiangan.py        # Heavenly Stems (天干), Ten Gods (十神)
│   ├── ganzhi.py         # Earthly Branches (地支), Nayin (纳音), Twelve Zhangsheng
│   ├── wuxing.py         # Five Elements (五行), YinYang
│   ├── trigram.py        # Eight Trigrams (八卦)
│   ├── daemon.py         # Gods/Deities (神煞)
│   ├── liushen.py        # Six Gods (六神)
│   └── relative.py       # Relative terms（六亲）
├── sixline/              # Six-line divination（六爻排盘）
│   ├── divinatory_symbol.py  # Divination symbol logic
│   └── output.py             # Six-line output formatting
└── birth_chart/              # Eight-character birth chart (八字排盘)
    ├── birth.py              # BirthChart class with assembly & analysis
    ├── output.py             # StandardBirthChartOutput schema
    └── geju.py               # Fortune pattern (格局) calculation
```

### Key Patterns

- **ValuedMultiton**: Base class in `base/symbol.py` for creating enum-like divination symbols with Chinese names
- **BirthChart.create()DivinatorySymbol.create()/**: Factory method that runs assemble() → analyze()

### Data Models

- `StandardBirthChartOutput`: Main output schema with personal_info, natal_chart, luck_cycles, target_flow, relations
- Uses Pydantic for validation
- tyme4py library for calendar calculations

## Key Files

- `base/symbol.py`:  all divination symbols are subclasses of ValuedMultiton, which provides a way to create enum-like classes with Chinese names and values.
- `birth_chart/birth.py`: birth chart（八字） assembly and analysis logic,
- `sixline/divinatory_symbol.py`: six-line（六爻） divination symbol generation and logic


## Coding Style & Naming Conventions
- Python 3.12+; follow standard PEP 8 with 4-space indentation.
- Use descriptive class names in `CapWords` and module/file names in `snake_case`.
- Tests follow `tests/test_*.py` naming; test classes are `Test*` and methods are `test_*`.

## Security & Configuration Tips
- Dependencies are defined in `pyproject.toml`; keep versions compatible with Python 3.12+.
- Avoid editing schema/data files unless updating corresponding tests.
