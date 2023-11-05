[![PyPi](https://img.shields.io/pypi/v/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![CI](https://img.shields.io/github/actions/workflow/status/heinrichreimer/warc-s3/ci.yml?branch=main&style=flat-square)](https://github.com/heinrichreimer/warc-s3/actions/workflows/ci.yml)
[![Code coverage](https://img.shields.io/codecov/c/github/heinrichreimer/warc-s3?style=flat-square)](https://codecov.io/github/heinrichreimer/warc-s3/)
[![Python](https://img.shields.io/pypi/pyversions/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![Issues](https://img.shields.io/github/issues/heinrichreimer/warc-s3?style=flat-square)](https://github.com/heinrichreimer/warc-s3/issues)
[![Commit activity](https://img.shields.io/github/commit-activity/m/heinrichreimer/warc-s3?style=flat-square)](https://github.com/heinrichreimer/warc-s3/commits)
[![Downloads](https://img.shields.io/pypi/dm/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![License](https://img.shields.io/github/license/heinrichreimer/warc-s3?style=flat-square)](LICENSE)

# 💾 warc-s3

Scalable and easy WARC records storage on S3.

## Installation
Install the package from PyPI:

```shell
pip install warc-s3
```

## Usage

TODO

## Development

To build this package and contribute to its development you need to install the `build`, and `setuptools` and `wheel` packages:

```shell
pip install build setuptools wheel
```

(On most systems, these packages are already pre-installed.)

### Installation

Install package and test dependencies:

```shell
pip install -e .[tests]
```

### Testing

Verify your changes against the test suite to verify.

```shell
flake8 warc_s3  # Code format
mypy warc_s3    # Static typing
pylint warc_s3  # LINT errors
bandit -c pyproject.toml -r warc_s3  # Security
pytest warc_s3  # Unit tests
```

Please also add tests for your newly developed code.

### Build wheels

Wheels for this package can be built with:

```shell
python -m build
```

## Support

If you hit any problems using this package, please file an [issue](https://github.com/heinrichreimer/warc-s3/issues/new).
We're happy to help!

## License

This repository is released under the [MIT license](LICENSE).
