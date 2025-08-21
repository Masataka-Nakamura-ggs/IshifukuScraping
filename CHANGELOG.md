# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-08-21

### Added
- Initial release of Ishifuku Gold Scraper
- Web scraping functionality for Ishifuku Metal Industry website
- Automatic gold price extraction and CSV export
- Comprehensive error handling and logging
- Log rotation by date
- Selenium WebDriver integration
- Comprehensive test suite with 92% coverage
- GitHub Actions CI/CD pipeline
- Modern Python project structure with pyproject.toml

### Features
- Scrapes gold retail prices from https://retail.ishifuku-kinzoku.co.jp/price/
- Saves data in CSV format with date, price, and timestamp
- Creates daily log files for errors and execution info
- Handles network errors and HTML structure changes gracefully
- Supports Python 3.8-3.13

### Testing
- 19 comprehensive test cases
- Unit tests for all core functions
- Integration tests for main workflow
- Selenium WebDriver mocking
- 92% code coverage

### Documentation
- Complete README with usage instructions
- Inline code documentation
- Project setup and development guide
