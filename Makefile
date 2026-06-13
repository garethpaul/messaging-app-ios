ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint test

lint test build: check

check:
	python3 "$(ROOT)/scripts/check-baseline.py"
