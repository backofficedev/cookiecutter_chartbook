"""doit task definitions for running tests and generating reports."""

import json
import shutil
import subprocess
from pathlib import Path

from dotenv import dotenv_values

OUTPUT_DIR = Path("_output")
EXAMPLE_DIR = Path("example")
TEMPLATE_DIR = Path("{{cookiecutter.project_slug}}")


def task_test():
    """Run pytest and save a JUnit XML report to _output/."""
    report_path = OUTPUT_DIR / "test_report.xml"
    return {
        "actions": [
            (OUTPUT_DIR.mkdir, [], {"parents": True, "exist_ok": True}),
            f"python -m pytest tests/ --junitxml={report_path} -v",
        ],
        "file_dep": [str(p) for p in TEMPLATE_DIR.rglob("*") if p.is_file()],
        "targets": [str(report_path)],
        "verbosity": 2,
    }


def task_example():
    """Generate a full example project in ./example/ using cookiecutter."""

    def generate_example():
        config = {
            "default_context": {
                "project_name": "Example",
                "project_slug": "example",
                "project_description": "Example project generated from cookiecutter-chartbook",
                "author_name": "Author Name",
                "author_email": "author@example.com",
                "python_version": "3.12",
                "environment_manager": "pip",
                "include_latex_reports": True,
                "include_jupyter_notebooks": True,
                "include_r_scripts": False,
                "include_stata_scripts": False,
                "include_chartbook": True,
                "include_github_actions": True,
                "include_fred": True,
                "include_fed_yield_curve": True,
                "include_ofr_api": True,
                "include_bloomberg": False,
                "include_crsp_stock": False,
                "include_crsp_compustat": True,
            }
        }

        config_path = OUTPUT_DIR / "example_cookiecutter_config.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2))

        # Remove existing example directory contents
        if EXAMPLE_DIR.exists():
            shutil.rmtree(EXAMPLE_DIR)

        # Generate into a temporary location, then move contents
        # Cookiecutter creates a subfolder named after project_slug
        result = subprocess.run(
            [
                "cookiecutter",
                ".",
                "--no-input",
                "--config-file",
                str(config_path),
                "--output-dir",
                str(OUTPUT_DIR),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"cookiecutter failed:\n{result.stdout}\n{result.stderr}"
            )

        generated = OUTPUT_DIR / "example"
        shutil.move(str(generated), str(EXAMPLE_DIR))

        # Remove ruff cache artifacts from the generated example
        for cache_dir in EXAMPLE_DIR.rglob(".ruff_cache"):
            shutil.rmtree(cache_dir)

    return {
        "actions": [generate_example],
        "verbosity": 2,
        "uptodate": [False],
    }


# def task_run_example():
#     """Run doit inside the generated example project."""

#     def run_example_doit():
#         import os

#         env = os.environ.copy()
#         env.update(dotenv_values(".env"))
#         result = subprocess.run(
#             ["doit", "-f", str(EXAMPLE_DIR / "dodo.py")],
#             capture_output=True,
#             text=True,
#             env=env,
#         )
#         print(result.stdout)
#         if result.stderr:
#             print(result.stderr)
#         if result.returncode != 0:
#             raise RuntimeError(f"doit in example/ failed (exit {result.returncode})")

#     return {
#         "actions": [run_example_doit],
#         "task_dep": ["example"],
#         "verbosity": 2,
#         "uptodate": [False],
#     }
