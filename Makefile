ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\n' "$$path" | sed 's/^ //'); dirname -- "$$path")

.PHONY: build check lint test

lint test build: check

check:
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/check-baseline.py"
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
