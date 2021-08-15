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
TEST_PATTERN?="test/**/*.lox"
test_clox: clox
	poetry run test ./clox $(TEST_PATTERN)

test_pylox:
	poetry run test ./pylox "test/bool/*" "test/comments/*" "test/operator/*" "test/nil/*" \
	  test/number/literals.lox test/empty_file.lox test/precedence.lox \
	  test/assignment/associativity.lox test/assignment/global.lox test/assignment/syntax.lox test/assignment/undefined.lox \
	  test/variable/redeclare_global.lox test/variable/redefine_global.lox /Users/drewthomas/Dev/lox/test/variable/undefined_global.lox \
	  test/variable/uninitialized.lox test/variable/use_global_in_initializer.lox


# Run tests for tooling.
test_tooling:
	cd tooling && poetry run pytest test

# Run all tests for clox and tooling.
test: test_clox test_tooling

.PHONY: clean clox debug test
