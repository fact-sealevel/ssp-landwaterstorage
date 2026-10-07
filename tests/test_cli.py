from click.testing import CliRunner

from ssp_landwaterstorage.cli import (
    main,
)


def test_main_fails_with_missing_required_arguments():
    """
    Test that the main function fails when required arguments are missing.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["--output-gslr-file", "output_gslr.nc"])
    assert result.exit_code != 0
    assert "Error: Missing option" in result.output


def test_main_shows_help_message():
    """
    Test that the main function shows the help message when --help is passed.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
