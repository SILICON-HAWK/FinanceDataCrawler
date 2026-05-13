#!/bin/bash

# Quick test script for local development
# Can be run outside of Docker

set -e

echo "=== Finance Data Crawler - Local Test Runner ==="
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "pipeline/test_harness.py" ]; then
    echo "Error: Run this script from the project root directory"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

echo "✓ Python3 available"

# Check if we can import required modules
echo "Checking imports..."
python3 -c "
import pipeline.config
import pipeline.utils.helpers
print('✓ Core modules imported successfully')
"

# Run individual tests
echo ""
echo "=== Running Component Tests ==="

for component in config utils storage queue_manager parsers; do
    echo "Testing $component..."
    python3 -c "
import sys
import unittest

# Add current directory to path
sys.path.insert(0, '.')

# Import test class
if '$component' == 'config':
    from pipeline.test_harness import TestConfig
elif '$component' == 'utils':
    from pipeline.test_harness import TestUtils
elif '$component' == 'storage':
    from pipeline.test_harness import TestStorage
elif '$component' == 'queue_manager':
    from pipeline.test_harness import TestQueueManager
elif '$component' == 'parsers':
    from pipeline.test_harness import TestParsers

# Create test suite
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(locals()[f'Test{component.capitalize()}']))

# Run test
runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
result = runner.run(suite)

# Output result
if result.wasSuccessful():
    print('✓ $component test passed')
else:
    print('✗ $component test failed')
    sys.exit(1)
"
done

echo ""
echo "=== Running Full Test Suite ==="
python3 pipeline/test_harness.py

echo ""
echo "=== Test Complete ==="