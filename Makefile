ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\n' "$$path" | sed 's/^ //'); dirname -- "$$path")

.PHONY: build check lint test

lint test build: check

check:
	/usr/bin/printf '%s  %s\n' '2627400b26522bcd2b17d56a93259f65fbc5a8f916739d0822e6ebae2b18279f' "$(ROOT)/scripts/verify-validation-chain.py" | /usr/bin/shasum -a 256 -c -
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/verify-validation-chain.py"
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/check-baseline.py"
	env -i HOME="$(HOME)" PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
