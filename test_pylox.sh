#!/usr/bin/env bash

# This script runs all tests for Pylox by invoking Python directly (rather than
# using Poetry). Starting Poetry is slow, so this cuts out a significant chunk of
# time when running all tests.
#
# See: https://github.com/python-poetry/poetry/issues/3502

set -euo pipefail

virtualenv_path=$(poetry show -v | grep "Using virtualenv" | sed "s/Using virtualenv: //")

source ${virtualenv_path}/bin/activate

python -m tooling.test_runner.cli ./pylox_test_cmd.sh \
	test/assignment/associativity.lox \
	test/assignment/global.lox \
	test/assignment/local.lox \
	test/assignment/syntax.lox \
	test/assignment/undefined.lox \
	"test/bool/*" \
	"test/block/*" \
	"test/call/*" \
	"test/class/*" \
	"test/closure/*" \
	"test/comments/*" \
	"test/constructor/*" \
	"test/field/*" \
	"test/for/*" \
	"test/function/*" \
	"test/if/*" \
	"test/inheritance/*" \
	"test/logical_operator/*" \
	"test/method/*" \
	"test/nil/*" \
	test/number/literals.lox \
	"test/operator/*" \
	"test/return/*" \
	test/string/literals.lox \
	"test/super/*" \
	"test/this/*" \
	test/variable/collide_with_parameter.lox \
	test/variable/duplicate_local.lox \
	test/variable/duplicate_parameter.lox \
	test/variable/early_bound.lox \
	test/variable/in_middle_of_block.lox \
	test/variable/in_nested_block.lox \
	test/variable/local_from_method.lox \
	test/variable/scope_reuse_in_different_blocks.lox \
	test/variable/shadow_and_local.lox \
	test/variable/shadow_global.lox \
	test/variable/shadow_local.lox \
	test/variable/undefined_local.lox \
	test/variable/redeclare_global.lox \
	test/variable/redefine_global.lox \
	test/variable/undefined_global.lox \
	test/variable/uninitialized.lox \
	test/variable/use_local_in_initializer.lox \
	test/variable/use_global_in_initializer.lox \
	"test/while/*" \
	test/empty_file.lox \
	test/precedence.lox
