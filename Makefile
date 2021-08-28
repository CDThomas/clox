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
	"test/assignment/*" \
	"test/bool/*" \
	"test/block/*" \
	"test/comments/*" \
	"test/nil/*" \
	"test/number/*" \
	"test/operator/*" \
	"test/print/*" \
	"test/string/*" \
	"test/variable/*" \
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
	"test/comments/*" \
	"test/for/*" \
	"test/if/*" \
	"test/logical_operator/*" \
	"test/nil/*" \
	test/number/literals.lox \
	"test/operator/*" \
	test/variable/in_middle_of_block.lox \
	test/variable/in_nested_block.lox \
	test/variable/scope_reuse_in_different_blocks.lox \
	test/variable/shadow_and_local.lox \
	test/variable/shadow_global.lox \
	test/variable/shadow_local.lox \
	test/variable/undefined_local.lox \
	test/variable/redeclare_global.lox \
	test/variable/redefine_global.lox \
	test/variable/undefined_global.lox \
	test/variable/uninitialized.lox \
	test/variable/use_global_in_initializer.lox \
	test/empty_file.lox \
	test/precedence.lox


# Run tests for tooling.
test_tooling:
	cd tooling && poetry run pytest test

# Run all tests for clox, pylox, and tooling.
test: test_clox test_pylox test_tooling

.PHONY: clean clox debug test
