# Test Guide

## Quick Start

### 1. Local Testing (No Docker Required)

```bash
# Run quick local tests
./test_local.sh

# Or run specific tests
python3 -m unittest pipeline.test_harness.TestConfig -v
python3 -m unittest pipeline.test_harness.TestUtils -v
python3 -m unittest pipeline.test_harness.TestStorage -v
```

### 2. Docker Testing

```bash
# Build test image
docker build -f Dockerfile.test -t finance-crawler-test .

# Run container tests
docker run --rm finance-crawler-test

# Or use docker-compose
docker-compose -f docker-compose.test.yml up test-runner

# Run individual test services
docker-compose -f docker-compose.test.yml up test-config
docker-compose -f docker-compose.test.yml up test-utils
docker-compose -f docker-compose.test.yml up test-storage
```

### 3. Full Test Suite

```bash
# Comprehensive test suite (requires dependencies)
python3 pipeline/test_harness.py
```

## Test Components

- **Configuration Tests**: Validate settings and constants
- **Utility Tests**: Text cleaning, data validation, helper functions  
- **Storage Tests**: JSON file operations and data persistence
- **Queue Manager Tests**: Sector/company queue operations
- **Parser Tests**: Sector and company data extraction
- **Crawler Tests**: HTTP requests with mocking
- **Integration Tests**: End-to-end pipeline validation

## Test Results

- **Console Output**: Real-time test progress and results
- **Test Reports**: JSON reports in `pipeline/test_report.json`
- **Error Details**: Detailed failure information for debugging

## Dependencies

Install required packages before running tests:
```bash
pip install -r requirements.txt
```

## Common Issues

1. **Import Errors**: Ensure you're in the project root directory
2. **Missing Dependencies**: Install requirements.txt
3. **Permission Issues**: Make scripts executable with `chmod +x test_local.sh`
4. **Docker Issues**: Ensure Docker is running and compose is installed