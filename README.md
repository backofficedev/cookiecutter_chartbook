# Economics/Finance Project Template

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter)-compatible template for creating reproducible data science projects with optional features for LaTeX reports, Jupyter notebooks, R scripts, Stata scripts, and various data sources.

We recommend using [cruft](https://cruft.github.io/cruft/) instead of cookiecutter to generate projects from this template. Cruft is fully compatible with cookiecutter templates but adds the ability to keep your project synchronized with template updates over time.

## Features

This template allows you to generate a customized data science project with:

- **Core Features** (always included):
  - PyDoit task runner for reproducible workflows
  - Python project structure with settings management
  - Git and environment configuration

- **Optional Features**:
  - LaTeX reports and slides (using custom templates)
  - Jupyter notebooks (stored as Python files using jupytext)
  - R scripts and RMarkdown files
  - Stata scripts
  - Chartbook documentation site
  - GitHub Actions CI/CD

- **Data Source Integration**:
  - FRED (Federal Reserve Economic Data)
  - OFR API (Office of Financial Research)
  - Bloomberg (requires terminal access)
  - CRSP Stock data (requires WRDS)
  - CRSP Compustat data (requires WRDS)

## Quick Start

### Prerequisites

1. Install [cruft](https://cruft.github.io/cruft/):
   ```bash
   pip install cruft
   ```

2. (Optional) Install [miniforge](https://github.com/conda-forge/miniforge) for conda environment management.

### Generate a New Project

```bash
cruft create https://github.com/backofficedev/cookiecutter_chartbook
```

This creates your project and a `.cruft.json` file that tracks the template version, enabling future updates.

You will be prompted for:
- Project name and description
- Author information
- Python version
- Which optional features to include
- Which data sources to include

### Updating Your Project

One of the key benefits of using cruft is the ability to update your project when the template changes:

```bash
# Check if your project is up-to-date with the template
cruft check

# View differences between your project and the latest template
cruft diff

# Update your project to the latest template version
cruft update
```

You can also add `cruft check` to your CI pipeline to ensure projects stay synchronized.

### Example Usage

```bash
# Generate with all defaults (interactive prompts)
cruft create https://github.com/backofficedev/cookiecutter_chartbook

# Generate with custom options
cruft create https://github.com/backofficedev/cookiecutter_chartbook \
  --no-input \
  -f \
  project_name="My Analysis" \
  include_latex_reports=y \
  include_fred=y
```

## Project Structure

The generated project will have this structure (files vary based on options):

```
my_project/
├── README.md
├── dodo.py                 # PyDoit task definitions
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment
├── .gitignore
├── .env.example
├── src/
│   ├── settings.py         # Configuration management
│   ├── misc_tools.py       # Utility functions
│   ├── pull_*.py           # Data pull scripts (based on selections)
│   ├── *_ipynb.py          # Notebook files (if selected)
│   └── ...
├── reports/                # LaTeX reports (if selected)
├── assets/                 # Static assets
├── data_manual/            # Version-controlled data
├── _data/                  # Downloaded data (gitignored)
├── _output/                # Generated outputs
└── .github/                # GitHub Actions (if selected)
```

## Running a Generated Project

After generating a project:

```bash
cd my_project

# Create and activate environment
conda create -n my_project python=3.12
conda activate my_project
pip install -r requirements.txt

# Run all tasks
doit

# List available tasks
doit list

# Run specific task
doit pull_fred
```

## Development

### Local Development Setup

When developing or testing the template locally, use `.` instead of the GitHub URL:

```bash
# Clone the repository
git clone https://github.com/backofficedev/cookiecutter_chartbook
cd cookiecutter_chartbook

# Generate a project from the local template to a specific output directory
cruft create . -o ./tmp/

# Or with no prompts (use defaults)
cruft create . --no-input -o ./tmp/

# Overwrite existing project with same name
cruft create . --no-input -o ./tmp/ --overwrite-if-exists
```

If you have an existing project that was created with cookiecutter, you can link it to the template:

```bash
cd my_existing_project
cruft link https://github.com/backofficedev/cookiecutter_chartbook
```

### Code Formatting

```bash
# Format code, sort imports, and fix linting issues
ruff format . && ruff check --select I --fix . && ruff check --fix .
```

### Running Template Tests

```bash
# Install test dependencies
pip install pytest cruft

# Run tests
pytest tests/ -v
```

### Testing Different Configurations

```bash
# Test minimal project (all features disabled)
cruft create . --no-input -o ./tmp/ \
  project_name="Minimal Test" \
  include_latex_reports=n \
  include_jupyter_notebooks=n \
  include_r_scripts=n \
  include_stata_scripts=n \
  include_chartbook=n \
  include_github_actions=n \
  include_fred=n \
  include_ofr_api=n \
  include_bloomberg=n \
  include_crsp_stock=n \
  include_crsp_compustat=n

# Test full project (all features enabled)
cruft create . --no-input -o ./tmp/ \
  project_name="Full Test" \
  include_latex_reports=y \
  include_jupyter_notebooks=y \
  include_r_scripts=y \
  include_stata_scripts=y \
  include_chartbook=y \
  include_github_actions=y \
  include_fred=y \
  include_ofr_api=y \
  include_bloomberg=y \
  include_crsp_stock=y \
  include_crsp_compustat=y

# Verify generated project works
cd ./tmp/minimal_test  # or ./tmp/full_test
doit list
```

## Example Project

The `example/` directory contains a full example of a generated project with all features enabled. This serves as a reference implementation.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
