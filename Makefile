.PHONY: __repository-make-authority build check lint test
.SECONDEXPANSION:

override SHELL := /bin/sh
override .SHELLFLAGS := -c
ifneq ($(origin -*-eval-flags-*-),undefined)
$(error --eval must not be used for repository verification)
endif
ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
override REPOSITORY_MAKE_BRACE := {
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value MAKEFILE_LIST)),)
$(error repository Makefile path must not contain Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_BRACE),$(value MAKEFILE_LIST)),)
$(error repository Makefile path must not contain Make syntax)
endif
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell sed_path=/usr/bin/sed; [ -x "$$sed_path" ] || sed_path=/bin/sed; [ -x "$$sed_path" ] || exit 1; path=$$(/usr/bin/printf '%s' '$(subst ','"'"',$(value MAKEFILE_LIST))' | "$$sed_path" 's/^ //'); [ -f "$$path" ] || exit 1; directory=$${path%/*}; [ "$$directory" != "$$path" ] || directory=.; CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif

build check lint test:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check lint test:: $$(if $$(shell sed_path=/usr/bin/sed && [ -x "$$$$sed_path" ] || sed_path=/bin/sed && [ -x "$$$$sed_path" ] && path=$$$$(printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | "$$$$sed_path" 's/^ //') && [ -f "$$$$path" ] && printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check lint test:: __repository-make-authority

__repository-make-authority::
	@:

lint:: check
test:: check
build:: check

check::
	/usr/bin/printf '%s  %s\n' '4dc5544a93e0055dc1eb2095b3ff2c331157b0565707dc4692f3922f5cd7386c' "$(ROOT)/scripts/verify-validation-chain.py" | /usr/bin/shasum -a 256 -c -
	/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/verify-validation-chain.py"
	/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" pre
	/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" test
	/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/check-baseline.py"
	/usr/bin/env -i HOME="$(HOME)" PATH="/usr/bin:/bin:/usr/sbin:/sbin" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I "$(ROOT)/scripts/run-isolated-tests.py" post
