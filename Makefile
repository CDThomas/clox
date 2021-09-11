# Makefile based on: https://github.com/munificent/craftinginterpreters/blob/3e5f0fa6636b68eddfe4dc0173af95130403f961/Makefile

BUILD_DIR := build

default: clox

# Compile a debug build of clox.
debug:
	@ $(MAKE) -f util/c.make NAME=cloxd MODE=debug SOURCE_DIR=c

# Compile the C interpreter.
clox:
	@ $(MAKE) -f util/c.make NAME=clox MODE=release SOURCE_DIR=c
	@ rm -f clox # Nuke the binary before copying (workaround for https://stackoverflow.com/questions/65258043/codesigning-modified-binaries-apple-silicon-m1)
	@ cp build/clox clox # For convenience, copy the interpreter to the top level.

# Remove all build outputs and intermediate files.
clean:
	rm -rf $(BUILD_DIR)

# Run tests for clox.
test_clox: clox
	@poetry run test ./clox \
	test/assignment/associativity.lox \
	test/assignment/global.lox \
	test/assignment/infix_operator.lox \
	test/assignment/local.lox \
	test/assignment/syntax.lox \
	test/assignment/undefined.lox \
	"test/bool/*" \
	"test/block/*" \
	"test/comments/*" \
	"test/nil/*" \
	"test/number/*" \
	test/operator/add.lox \
	test/operator/add_bool_nil.lox \
	test/operator/add_bool_num.lox \
	test/operator/add_bool_string.lox \
	test/operator/add_nil_nil.lox \
	test/operator/add_num_nil.lox \
	test/operator/add_string_nil.lox \
	test/operator/comparison.lox \
	test/operator/divide.lox \
	test/operator/divide_nonnum_num.lox \
	test/operator/divide_num_nonnum.lox \
	test/operator/equals.lox \
	test/operator/greater_nonnum_num.lox \
	test/operator/greater_num_nonnum.lox \
	test/operator/greater_or_equal_nonnum_num.lox \
	test/operator/greater_or_equal_num_nonnum.lox \
	test/operator/less_nonnum_num.lox \
	test/operator/less_num_nonnum.lox \
	test/operator/less_or_equal_nonnum_num.lox \
	test/operator/less_or_equal_num_nonnum.lox \
	test/operator/multiply.lox \
	test/operator/multiply_nonnum_num.lox \
	test/operator/multiply_num_nonnum.lox \
	test/operator/negate.lox \
	test/operator/negate_nonnum.lox \
	test/operator/not.lox \
	test/operator/not_equals.lox \
	test/operator/subtract.lox \
	test/operator/subtract_nonnum_num.lox \
	test/operator/subtract_num_nonnum.lox \
	"test/print/*" \
	"test/string/*" \
	test/variable/duplicate_local.lox \
	test/variable/in_middle_of_block.lox \
	test/variable/in_nested_block.lox \
	test/variable/redeclare_global.lox \
	test/variable/redefine_global.lox \
	test/variable/scope_reuse_in_different_blocks.lox \
	test/variable/shadow_and_local.lox \
	test/variable/shadow_global.lox \
	test/variable/shadow_local.lox \
	test/variable/undefined_global.lox \
	test/variable/undefined_local.lox \
	test/variable/uninitialized.lox \
	test/variable/use_false_as_var.lox \
	test/variable/use_global_in_initializer.lox \
	test/variable/use_local_in_initializer.lox \
	test/variable/use_nil_as_var.lox \
	test/variable/use_this_as_var.lox \
	test/empty_file.lox \
	test/precedence.lox

test_pylox:
	@poetry run test ./pylox \
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
	"test/logical_operator/*" \
	"test/method/*" \
	"test/nil/*" \
	test/number/literals.lox \
	"test/operator/*" \
	"test/return/*" \
	test/string/literals.lox \
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

# Run tests for tooling.
test_tooling:
	cd tooling && poetry run pytest test

# Run all tests for clox, pylox, and tooling.
test: test_clox test_pylox test_tooling

typecheck_pylox:
	poetry run mypy ./python

typecheck_tooling:
	poetry run mypy ./tooling

typecheck: typecheck_pylox typecheck_tooling

.PHONY: clean clox debug test typecheck
