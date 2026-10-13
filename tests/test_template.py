"""Tests for the cruft/cookiecutter template.

These tests verify that the template generates valid projects with
different combinations of options.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter


# Base context with all features disabled (uses pip by default)
MINIMAL_CONTEXT = {
    "project_name": "Test Project",
    "project_slug": "test_project",
    "project_description": "A test project",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "python_version": "3.12",
    "environment_manager": "pip",
    "include_latex_reports": False,
    "include_jupyter_notebooks": False,
    "include_r_scripts": False,
    "include_stata_scripts": False,
    "include_chartbook": False,
    "include_github_actions": False,
    "include_fred": False,
    "include_fed_yield_curve": False,
    "include_ofr_api": False,
    "include_bloomberg": False,
    "include_crsp_stock": False,
    "include_crsp_compustat": False,
}

# Full context with all features enabled (uses conda for R support)
FULL_CONTEXT = {
    **MINIMAL_CONTEXT,
    "environment_manager": "conda",  # Required for R scripts
    "include_latex_reports": True,
    "include_jupyter_notebooks": True,
    "include_r_scripts": True,
    "include_stata_scripts": True,
    "include_chartbook": True,
    "include_github_actions": True,
    "include_fred": True,
    "include_fed_yield_curve": True,
    "include_ofr_api": True,
    "include_bloomberg": True,
    "include_crsp_stock": True,
    "include_crsp_compustat": True,
}


def generate_project(template_dir, output_dir, context):
    """Generate a project from the template using cookiecutter."""
    return cookiecutter(
        str(template_dir),
        output_dir=str(output_dir),
        no_input=True,
        extra_context=context,
    )


def test_minimal_project_generation(template_dir, temp_dir):
    """Test generating a minimal project with all optional features disabled."""
    project_path = generate_project(template_dir, temp_dir, MINIMAL_CONTEXT)
    project_dir = Path(project_path)

    # Core files should exist
    assert (project_dir / "README.md").exists()
    assert (project_dir / "dodo.py").exists()
    assert (project_dir / "requirements.txt").exists()  # pip uses requirements.txt
    assert (project_dir / ".gitignore").exists()
    assert (project_dir / "src" / "settings.py").exists()
    assert (project_dir / "src" / "misc_tools.py").exists()

    # Environment files for other managers should NOT exist (pip is default)
    assert not (project_dir / "environment.yml").exists()
    assert not (project_dir / "pyproject.toml").exists()
    assert not (project_dir / "pixi.toml").exists()

    # Optional files should NOT exist
    assert not (project_dir / "reports").exists()
    assert not (project_dir / "chartbook.toml").exists()
    assert not (project_dir / "docs_src").exists()
    assert not (project_dir / ".github").exists()
    assert not (project_dir / "r_requirements.txt").exists()
    assert not (project_dir / ".latexmkrc").exists()

    # Data pull scripts should NOT exist
    assert not (project_dir / "src" / "pull_fred.py").exists()
    assert not (project_dir / "src" / "pull_ofr_api_data.py").exists()
    assert not (project_dir / "src" / "pull_bloomberg.py").exists()

    # example_plot.py only belongs with FRED or the LaTeX reports
    assert not (project_dir / "src" / "example_plot.py").exists()

    # Only the R and Stata examples need directories defined in .env
    assert "DATA_DIR" not in (project_dir / ".env.example").read_text()


def test_full_project_generation(template_dir, temp_dir):
    """Test generating a full project with all optional features enabled."""
    project_path = generate_project(template_dir, temp_dir, FULL_CONTEXT)
    project_dir = Path(project_path)

    # Core files should exist
    assert (project_dir / "README.md").exists()
    assert (project_dir / "dodo.py").exists()
    assert (project_dir / "requirements.txt").exists()

    # Optional files should exist
    assert (project_dir / "reports").exists()
    assert (project_dir / "chartbook.toml").exists()
    assert (project_dir / "docs_src").exists()
    assert (project_dir / ".github").exists()
    assert (project_dir / "r_requirements.txt").exists()
    assert (project_dir / ".latexmkrc").exists()

    # Site pages should exist
    site_dir = project_dir / "docs_src" / "site"
    assert (site_dir / "index_toc.md").exists()
    assert (site_dir / "project_overview.md").exists()
    assert (site_dir / "project_overview" / "goals.md").exists()
    assert (site_dir / "project_overview" / "data_sources.md").exists()
    assert (site_dir / "project_overview" / "methodology.md").exists()

    # Data pull scripts should exist
    assert (project_dir / "src" / "pull_fred.py").exists()
    assert (project_dir / "src" / "pull_ofr_api_data.py").exists()
    assert (project_dir / "src" / "pull_bloomberg.py").exists()
    assert (project_dir / "src" / "pull_CRSP_stock.py").exists()
    assert (project_dir / "src" / "pull_CRSP_Compustat.py").exists()

    # Notebooks should exist
    assert (project_dir / "src" / "01_example_notebook_interactive.ipynb.py").exists()
    assert (project_dir / "src" / "02_example_with_dependencies.ipynb.py").exists()
    assert (project_dir / "src" / "03_public_repo_summary_charts.ipynb.py").exists()

    # R files should exist
    assert (project_dir / "src" / "example_r_plot.r").exists()
    assert (project_dir / "src" / "install_packages.r").exists()
    assert (project_dir / "src" / "04_example_regressions.Rmd").exists()

    # Stata files should exist
    assert (project_dir / "src" / "example_stata_plot.do").exists()


def test_notebooks_with_fred_only(template_dir, temp_dir):
    """Test that notebook 02 is included when FRED is selected, but not notebook 03."""
    context = {
        **MINIMAL_CONTEXT,
        "include_jupyter_notebooks": True,
        "include_fred": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # Notebook 01 should exist (no dependencies)
    assert (project_dir / "src" / "01_example_notebook_interactive.ipynb.py").exists()
    # Notebook 02 should exist (requires FRED)
    assert (project_dir / "src" / "02_example_with_dependencies.ipynb.py").exists()
    # Notebook 03 should NOT exist (requires FRED + OFR)
    assert not (project_dir / "src" / "03_public_repo_summary_charts.ipynb.py").exists()
    # example_plot.py should exist (it plots FRED data)
    assert (project_dir / "src" / "example_plot.py").exists()


def test_notebooks_with_fred_and_ofr(template_dir, temp_dir):
    """Test that all notebooks are included when FRED and OFR are selected."""
    context = {
        **MINIMAL_CONTEXT,
        "include_jupyter_notebooks": True,
        "include_fred": True,
        "include_ofr_api": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # All notebooks should exist
    assert (project_dir / "src" / "01_example_notebook_interactive.ipynb.py").exists()
    assert (project_dir / "src" / "02_example_with_dependencies.ipynb.py").exists()
    assert (project_dir / "src" / "03_public_repo_summary_charts.ipynb.py").exists()


def test_latex_only(template_dir, temp_dir):
    """Test generating a project with only LaTeX reports."""
    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert (project_dir / "reports").exists()
    assert (project_dir / ".latexmkrc").exists()
    assert (project_dir / "src" / "example_table.py").exists()
    assert (project_dir / "src" / "example_plot.py").exists()
    assert (project_dir / "src" / "pandas_to_latex_demo.py").exists()


def test_latex_reports_avoid_eps_graphics(template_dir, temp_dir):
    """Test that the reports don't include EPS figures.

    pdfLaTeX, the default engine in most editors, can only use EPS by converting
    it on the fly. Default (restricted shell escape) settings refuse to write the
    converted file outside the document's directory, so the build fails.
    """
    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    for tex_file in (project_dir / "reports").glob("*.tex"):
        graphics = re.findall(
            r"\\includegraphics(?:ifexists)?(?:\[[^\]]*\])?\{([^}]+)\}",
            tex_file.read_text(),
        )
        eps_graphics = [g for g in graphics if g.lower().endswith(".eps")]
        assert not eps_graphics, f"{tex_file.name} includes EPS: {eps_graphics}"

    assert (project_dir / "assets" / "star_network_n_nodes.pdf").exists()


def test_latex_reports_guard_generated_outputs(template_dir, temp_dir):
    """Test that reports only include pipeline outputs after checking they exist.

    A plain \\input or \\includegraphics of a file in _output is a fatal error
    until doit has been run, which is what a new user hits on their first build.
    """
    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    for tex_file in (project_dir / "reports").glob("*.tex"):
        text = tex_file.read_text()
        checked = set(re.findall(r"\\IfFileExists\{([^}]+)\}", text))
        included = re.findall(
            r"\\(?:input|includegraphics(?:\[[^\]]*\])?)"
            r"\{((?:\\PathToOutput|\.\./_output)/[^}]+)\}",
            text,
        )
        unchecked = [path for path in included if path not in checked]
        assert not unchecked, f"{tex_file.name} includes unchecked outputs: {unchecked}"

    # doit, unlike an editor, must still build the outputs before compiling
    dodo = (project_dir / "dodo.py").read_text()
    for output in ["example_plot.png", "example_table.tex", "pandas_to_latex_simple_table1.tex"]:
        assert f'OUTPUT_DIR / "{output}",' in dodo


@pytest.mark.integration
def test_latex_reports_compile_before_outputs_exist(template_dir, temp_dir):
    """Integration test: compile the reports with pdfLaTeX on a brand-new project.

    This is what an editor's build button does before doit has been run.
    """
    if shutil.which("latexmk") is None or shutil.which("pdflatex") is None:
        pytest.skip("requires latexmk and pdflatex")

    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    reports_dir = Path(project_path) / "reports"

    for name in ["report_example", "slides_example", "report_simple_example"]:
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"],
            cwd=reports_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{name} failed to compile:\n{result.stdout[-3000:]}"
        assert (reports_dir / f"{name}.pdf").exists()


def test_latex_without_fred_has_no_fred_dependency(template_dir, temp_dir):
    """Test that the LaTeX example inputs don't need FRED when it isn't selected.

    The .tex files are copied without rendering, so they always include
    example_plot.png and example_table.tex. Both must be buildable without
    pull_fred.py, which is removed when FRED is not selected.
    """
    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert not (project_dir / "src" / "pull_fred.py").exists()
    for script in ["example_plot.py", "example_table.py"]:
        assert "import pull_fred" not in (project_dir / "src" / script).read_text()

    dodo = (project_dir / "dodo.py").read_text()
    assert "def task_example_plot" in dodo
    assert "pull_fred" not in dodo


@pytest.mark.integration
def test_latex_examples_run_without_fred(template_dir, temp_dir):
    """Integration test: build the LaTeX example inputs with FRED not selected."""
    for package in ["decouple", "matplotlib", "numpy", "pandas", "seaborn"]:
        pytest.importorskip(package)

    context = {
        **MINIMAL_CONTEXT,
        "include_latex_reports": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "config", "summary_stats", "example_plot"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit failed: {result.stderr}\n{result.stdout}"
    output_dir = project_dir / "_output"
    assert (output_dir / "example_plot.png").exists()
    assert (output_dir / "example_table.tex").exists()
    assert (output_dir / "pandas_to_latex_simple_table1.tex").exists()


def test_r_only(template_dir, temp_dir):
    """Test generating a project with only R scripts."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "conda",  # R requires conda or pixi
        "include_r_scripts": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert (project_dir / "r_requirements.txt").exists()
    assert (project_dir / "src" / "example_r_plot.r").exists()
    assert (project_dir / "src" / "install_packages.r").exists()
    assert (project_dir / "src" / "04_example_regressions.Rmd").exists()
    # Conda projects should have environment.yml
    assert (project_dir / "environment.yml").exists()
    # The R examples read these directories from .env
    env_example = (project_dir / ".env.example").read_text()
    assert "DATA_DIR=_data" in env_example
    assert "OUTPUT_DIR=_output" in env_example


def test_stata_only(template_dir, temp_dir):
    """Test generating a project with only Stata scripts."""
    context = {
        **MINIMAL_CONTEXT,
        "include_stata_scripts": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert (project_dir / "src" / "example_stata_plot.do").exists()
    # The Stata example reads these directories from .env
    env_example = (project_dir / ".env.example").read_text()
    assert "DATA_DIR=_data" in env_example
    assert "OUTPUT_DIR=_output" in env_example


def test_r_without_fred_has_no_fred_dependency(template_dir, temp_dir):
    """Test that the R examples don't read FRED data when FRED isn't selected."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "conda",  # R requires conda or pixi
        "include_r_scripts": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    for script in ["example_r_plot.r", "04_example_regressions.Rmd"]:
        assert "fred.parquet" not in (project_dir / "src" / script).read_text()
    assert "pull_fred" not in (project_dir / "dodo.py").read_text()


def test_stata_without_fred_has_no_fred_dependency(template_dir, temp_dir):
    """Test that the Stata example doesn't read FRED data when FRED isn't selected."""
    context = {
        **MINIMAL_CONTEXT,
        "include_stata_scripts": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert "fred.csv" not in (project_dir / "src" / "example_stata_plot.do").read_text()
    assert "pull_fred" not in (project_dir / "dodo.py").read_text()


def test_wrds_sources(template_dir, temp_dir):
    """Test generating a project with WRDS data sources."""
    context = {
        **MINIMAL_CONTEXT,
        "include_crsp_stock": True,
        "include_crsp_compustat": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    assert (project_dir / "src" / "pull_CRSP_stock.py").exists()
    assert (project_dir / "src" / "pull_CRSP_Compustat.py").exists()

    # Check requirements.txt includes wrds
    requirements = (project_dir / "requirements.txt").read_text()
    assert "wrds" in requirements


def test_dodo_py_syntax(template_dir, temp_dir):
    """Test that generated dodo.py has valid Python syntax."""
    project_path = generate_project(template_dir, temp_dir, FULL_CONTEXT)
    project_dir = Path(project_path)

    dodo_path = project_dir / "dodo.py"
    assert dodo_path.exists()

    # Check Python syntax by compiling
    import py_compile

    try:
        py_compile.compile(str(dodo_path), doraise=True)
    except py_compile.PyCompileError as e:
        pytest.fail(f"dodo.py has invalid Python syntax: {e}")


def test_dodo_src_references_match_filenames(template_dir, temp_dir):
    """Test that every src file named in dodo.py exists with that exact case.

    Compares against the directory listing rather than using exists(), so a
    case mismatch is caught on case-insensitive filesystems too.
    """
    project_path = generate_project(template_dir, temp_dir, FULL_CONTEXT)
    project_dir = Path(project_path)

    src_files = set(os.listdir(project_dir / "src"))
    referenced = set(re.findall(r"\./src/([\w.]+)", (project_dir / "dodo.py").read_text()))

    assert referenced, "expected dodo.py to reference files in ./src"
    assert referenced <= src_files, f"not found in src/: {sorted(referenced - src_files)}"


def test_doit_list_command(template_dir, temp_dir):
    """Test that 'doit list' runs successfully on the generated project."""
    project_path = generate_project(template_dir, temp_dir, MINIMAL_CONTEXT)
    project_dir = Path(project_path)

    # Run doit list to verify the dodo.py is valid
    result = subprocess.run(
        ["doit", "list"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    # doit list should succeed (return code 0)
    assert result.returncode == 0, f"doit list failed: {result.stderr}"


def test_doit_list_with_chartbook(template_dir, temp_dir):
    """Test that 'doit list' runs successfully when chartbook is enabled."""
    context = {
        **MINIMAL_CONTEXT,
        "include_chartbook": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "list"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit list failed: {result.stderr}"


def test_doit_list_with_fred(template_dir, temp_dir):
    """Test that 'doit list' runs successfully with FRED enabled."""
    context = {
        **MINIMAL_CONTEXT,
        "include_fred": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "list"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit list failed: {result.stderr}"


def test_doit_task_dependencies_resolve(template_dir, temp_dir):
    """Test that every task_dep in the full project names a task that exists.

    'doit list' doesn't check task_dep, but running any task does, so run the
    lightweight config task.
    """
    project_path = generate_project(template_dir, temp_dir, FULL_CONTEXT)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "config"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit config failed: {result.stderr}"


def test_readme_contains_project_name(template_dir, temp_dir):
    """Test that README.md contains the project name."""
    context = {
        **MINIMAL_CONTEXT,
        "project_name": "My Awesome Project",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    readme = (project_dir / "README.md").read_text()
    assert "My Awesome Project" in readme


@pytest.mark.skip(
    reason="pandas-datareader incompatible with pandas>=2.2 (deprecate_kwarg signature change). "
    "See: https://github.com/pydata/pandas-datareader/issues"
)
@pytest.mark.integration
def test_doit_runs_with_fred(template_dir, temp_dir):
    """Integration test: generate project with FRED and run doit.

    This test creates a conda environment with Python and pip installs
    requirements, then runs doit to verify the full pipeline works end-to-end.
    """
    context = {
        **MINIMAL_CONTEXT,
        "include_fred": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # Create conda env and run doit
    env_name = f"test_env_{os.getpid()}"
    try:
        # Create a minimal conda environment with just Python
        create_result = subprocess.run(
            ["conda", "create", "-n", env_name, "python=3.12", "-y"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for env creation
        )
        if create_result.returncode != 0:
            pytest.fail(f"Failed to create conda env: {create_result.stderr}")

        # Install requirements via pip
        pip_result = subprocess.run(
            ["conda", "run", "-n", env_name, "pip", "install", "-r", "requirements.txt"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for pip install
        )
        if pip_result.returncode != 0:
            pytest.fail(f"Failed to pip install: {pip_result.stderr}")

        # Run doit in the conda environment
        result = subprocess.run(
            ["conda", "run", "-n", env_name, "doit"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for doit
        )

        assert result.returncode == 0, f"doit failed: {result.stderr}\n{result.stdout}"
    finally:
        # Cleanup: remove conda environment
        subprocess.run(
            ["conda", "env", "remove", "-n", env_name, "-y"],
            capture_output=True,
        )


# ============================================================================
# Environment Manager Tests
# ============================================================================


def test_environment_manager_pip(template_dir, temp_dir):
    """Test that pip environment manager creates correct files."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "pip",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # pip should have requirements.txt only
    assert (project_dir / "requirements.txt").exists()
    assert not (project_dir / "environment.yml").exists()
    assert not (project_dir / "pyproject.toml").exists()
    assert not (project_dir / "pixi.toml").exists()

    # Check README mentions pip
    readme = (project_dir / "README.md").read_text()
    assert "python -m venv" in readme
    assert "pip install -r requirements.txt" in readme


def test_environment_manager_uv(template_dir, temp_dir):
    """Test that uv environment manager creates correct files."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "uv",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # uv should have pyproject.toml only
    assert (project_dir / "pyproject.toml").exists()
    assert not (project_dir / "requirements.txt").exists()
    assert not (project_dir / "environment.yml").exists()
    assert not (project_dir / "pixi.toml").exists()

    # Check pyproject.toml has correct structure
    pyproject = (project_dir / "pyproject.toml").read_text()
    assert "[project]" in pyproject
    assert "dependencies" in pyproject
    assert "[tool.pytest.ini_options]" in pyproject

    # Check README mentions uv
    readme = (project_dir / "README.md").read_text()
    assert "uv sync" in readme


def test_environment_manager_conda(template_dir, temp_dir):
    """Test that conda environment manager creates correct files."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "conda",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # conda should have environment.yml and requirements.txt
    assert (project_dir / "environment.yml").exists()
    assert (project_dir / "requirements.txt").exists()
    assert not (project_dir / "pyproject.toml").exists()
    assert not (project_dir / "pixi.toml").exists()

    # Check README mentions conda
    readme = (project_dir / "README.md").read_text()
    assert "conda env create" in readme


def test_environment_manager_pixi(template_dir, temp_dir):
    """Test that pixi environment manager creates correct files."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "pixi",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # pixi should have pixi.toml and requirements.txt
    assert (project_dir / "pixi.toml").exists()
    assert (project_dir / "requirements.txt").exists()
    assert not (project_dir / "environment.yml").exists()
    assert not (project_dir / "pyproject.toml").exists()

    # Check pixi.toml has correct structure
    pixi_toml = (project_dir / "pixi.toml").read_text()
    assert "[project]" in pixi_toml
    assert "[dependencies]" in pixi_toml
    assert "[tasks]" in pixi_toml

    # Check README mentions pixi
    readme = (project_dir / "README.md").read_text()
    assert "pixi install" in readme


def test_r_with_pip_fails(template_dir, temp_dir):
    """Test that R scripts with pip environment manager fails validation."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "pip",
        "include_r_scripts": True,
    }

    with pytest.raises(Exception) as exc_info:
        generate_project(template_dir, temp_dir, context)

    # Should fail due to pre-gen hook validation
    assert "Hook script failed" in str(exc_info.value) or "FailedHookException" in str(
        type(exc_info.value).__name__
    )


def test_r_with_uv_fails(template_dir, temp_dir):
    """Test that R scripts with uv environment manager fails validation."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "uv",
        "include_r_scripts": True,
    }

    with pytest.raises(Exception) as exc_info:
        generate_project(template_dir, temp_dir, context)

    # Should fail due to pre-gen hook validation
    assert "Hook script failed" in str(exc_info.value) or "FailedHookException" in str(
        type(exc_info.value).__name__
    )


def test_r_with_pixi_works(template_dir, temp_dir):
    """Test that R scripts with pixi environment manager works."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "pixi",
        "include_r_scripts": True,
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    # Should have R files and pixi.toml
    assert (project_dir / "r_requirements.txt").exists()
    assert (project_dir / "pixi.toml").exists()
    assert (project_dir / "src" / "example_r_plot.r").exists()

    # Check pixi.toml includes R dependencies
    pixi_toml = (project_dir / "pixi.toml").read_text()
    assert "r-base" in pixi_toml


def test_doit_list_with_uv(template_dir, temp_dir):
    """Test that 'doit list' runs successfully with uv environment manager."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "uv",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "list"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit list failed: {result.stderr}"


def test_doit_list_with_pixi(template_dir, temp_dir):
    """Test that 'doit list' runs successfully with pixi environment manager."""
    context = {
        **MINIMAL_CONTEXT,
        "environment_manager": "pixi",
    }
    project_path = generate_project(template_dir, temp_dir, context)
    project_dir = Path(project_path)

    result = subprocess.run(
        ["doit", "list"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"doit list failed: {result.stderr}"
