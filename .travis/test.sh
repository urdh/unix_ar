#!/bin/sh

set -eux

case "$TEST_MODE"
in
    run_tests)
        python tests.py
        ;;
    check_style)
        flake8 --ignore=E731 unix_ar.py setup.py tests.py
        ;;
    coverage)
        coverage run --source=unix_ar.py --branch tests.py
        ;;
esac
