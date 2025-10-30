# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automated testing and coverage reporting in CI. Status badges on README.

### Changed

- Removed the `--includepokherl` CLI option. This is a breaking change ([PR #8](https://github.com/fact-sealevel/ssp-landwaterstorage/pull/8); [@brews](https://github.com/brews)).
- Heavy internal refactoring to improve code clarity and testability ([PR #8](https://github.com/fact-sealevel/ssp-landwaterstorage/pull/8); [@brews](https://github.com/brews)).

### Fixed

- GWD files may not have been used when used with the `--includepokherl` option ([PR #8](https://github.com/fact-sealevel/ssp-landwaterstorage/pull/8); [@brews](https://github.com/brews)).
- Bad release hyperlinks in CHANGELOG.


## [0.2.0] - 2025-10-27

### Added

- Build multiplatform container images. We're now experimenting with support for linux/arm64, in addition to linux/amd64.

### Changed

- Update docs to use public `ghcr.io/fact-sealevel/ssp-landwaterstorage` container image at new host Github organization. THIS IS A BREAKING CHANGE.

- Update README and docs to use new repository URL at github.com/fact-sealevel/ssp-landwaterstorage.


## [0.1.0] - 2025-06-03

- Initial release.


[Unreleased]: https://github.com/fact-sealevel/ssp-landwaterstorage/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/fact-sealevel/ssp-landwaterstorage/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/fact-sealevel/ssp-landwaterstorage/releases/tag/v0.1.0
