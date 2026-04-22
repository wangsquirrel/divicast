# Repository Guidelines

This file provides guidance to coding agent(like claude or codex) when working with code in this repository.

## Project Overview

Divicast is a Chinese metaphysics(玄学) library that provides programmatic chart generation for various traditional divination systems.. Currently supports:
- **六爻 (Six-line divination)**: Core divination system
- **八字 (Eight-character birth chart)**: Natal chart analysis including fortune cycles, patterns (格局)

Goal: Provide all mainstream Chinese divination systems as a library, published to PyPI.

## Commands

```bash
# Install dependencies with uv
uv sync

# Run python with uv to ensure correct environment
uv run python ... # run python file or snippets. Never use plain python/python3 in this repository

# Run all tests
uv run python -m unittest

# CI uses the same unit test command after syncing the test group
uv sync --group test && uv run python -m unittest

# Run a specific test file
uv run python -m unittest tests.test_geju

# Run examples
uv run python examples/sixline_example.py
uv run python examples/bazi_example.py

# Build and publish to PyPI

uv cache clean # clean uv cache s
uv build # build source distribution and wheel, outputs to dist/
twine upload dist/* # publish to PyPI, requires ~/.pypirc with PyPI credentials
```



## Code Architecture

### Source Structure

```
src/divicast/
├── base/
│   └── symbol.py         # Base ValuedMultiton class for enum-like divination symbols
├── entities/             # Core data models and logic for all divination systems
│   ├── ganzhi.py         # Heavenly Stems (天干), Earthly Branches (地支), Ten Gods (十神), Nayin (纳音), Twelve Zhangsheng
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
    └── ...                   # Other files for 八字排盘
```

### Key Patterns

- **ValuedMultiton**: Base class in `base/symbol.py` for creating enum-like divination symbols with Chinese names
- **BirthChart.create()DivinatorySymbol.create()/**: Factory method that runs assemble() → analyze()
- Entity symbol classes must keep a single canonical implementation. Do not keep duplicate `ValuedMultiton` subclasses in multiple modules.

### Data Models

- `StandardBirthChartOutput`: Main output schema with personal_info, natal_chart, luck_cycles, target_flow, relations
- Uses Pydantic for validation
- tyme4py library for calendar calculations

## Key Files

- `base/symbol.py`:  all divination symbols are subclasses of ValuedMultiton, which provides a way to create enum-like classes with Chinese names and values.
- `birth_chart/birth.py`: birth chart（八字） assembly and analysis logic,
- `docs/bazi_module.md`: birth chart（八字） module design, capabilities, output structure, test coverage and edge cases.
- `sixline/divinatory_symbol.py`: six-line（六爻） divination symbol generation and logic
- `docs/sixline_module.md`: six-line divination module design, capabilities, output structure, test coverage and edge cases.


## Coding Style & Naming Conventions
- Python 3.12+; follow standard PEP 8 with 4-space indentation.
- Use descriptive class names in `CapWords` and module/file names in `snake_case`.
- Tests follow `tests/test_*.py` naming; test classes are `Test*` and methods are `test_*`.

## Security & Configuration Tips
- Dependencies are defined in `pyproject.toml`; keep versions compatible with Python 3.12+.
- `tyme4py` is pinned because 八字 golden tests depend on exact calendar/solar-term boundary behavior; update fixtures and boundary tests deliberately when changing it.
- Runtime package version is read from package metadata in `src/divicast/__init__.py`; update `pyproject.toml` rather than hard-coding `__version__`.
- Avoid editing schema/data files unless updating corresponding tests.
