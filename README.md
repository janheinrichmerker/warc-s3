[![PyPi](https://img.shields.io/pypi/v/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![CI](https://img.shields.io/github/actions/workflow/status/janheinrichmerker/warc-s3/ci.yml?branch=main&style=flat-square)](https://github.com/janheinrichmerker/warc-s3/actions/workflows/ci.yml)
[![Code coverage](https://img.shields.io/codecov/c/github/janheinrichmerker/warc-s3?style=flat-square)](https://codecov.io/github/janheinrichmerker/warc-s3/)
[![Python](https://img.shields.io/pypi/pyversions/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![Issues](https://img.shields.io/github/issues/janheinrichmerker/warc-s3?style=flat-square)](https://github.com/janheinrichmerker/warc-s3/issues)
[![Commit activity](https://img.shields.io/github/commit-activity/m/janheinrichmerker/warc-s3?style=flat-square)](https://github.com/janheinrichmerker/warc-s3/commits)
[![Downloads](https://img.shields.io/pypi/dm/warc-s3?style=flat-square)](https://pypi.org/project/warc-s3/)
[![License](https://img.shields.io/github/license/janheinrichmerker/warc-s3?style=flat-square)](LICENSE)

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

Then, install the package and test dependencies:

```shell
pip install -e .[tests]
```

You can now verify your changes against the test suite.

```shell
ruff check .                   # Code format and LINT
mypy .                         # Static typing
bandit -c pyproject.toml -r .  # Security
pytest .                       # Unit tests
```

Please also add tests for your newly developed code.

### Build wheels

Wheels for this package can be built with:

```shell
python -m build
```

## Support

If you hit any problems using this package, please file an [issue](https://github.com/janheinrichmerker/warc-s3/issues/new).
We're happy to help!

## License

This repository is released under the [MIT license](LICENSE).
