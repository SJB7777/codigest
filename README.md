# CodeInspector

CodeInspector is a Python package and CLI tool for evaluating Python project quality.

## Features
- Cyclomatic Complexity Analysis
- Maintainability Index
- Flake8 style violation count
- .gitignore-aware file filtering
- Optional profiling with `profiling.log`
- Source code gathering

## Installation
```bash
pip install .
```

## Usage
```bash
codeinspector ./my_project --gather all_code.txt --profile
```

## As a Module
```python
from codeinspector.cli import run_analysis
results = run_analysis("./my_project")
```

## Requirements
- Python >= 3.10

### LICENSE
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
