# Makefile based on: https://github.com/munificent/craftinginterpreters/blob/3e5f0fa6636b68eddfe4dc0173af95130403f961/Makefile

BUILD_DIR := build

default: clox

# Compile a debug build of clox.
debug:
	@ $(MAKE) -f util/c.make NAME=cloxd MODE=debug SOURCE_DIR=src

# Compile the C interpreter.
clox:
	@ $(MAKE) -f util/c.make NAME=clox MODE=release SOURCE_DIR=src
	@ rm -f clox # Nuke the binary before copying (workaround for https://stackoverflow.com/questions/65258043/codesigning-modified-binaries-apple-silicon-m1)
	@ cp build/clox clox # For convenience, copy the interpreter to the top level.

# Remove all build outputs and intermediate files.
clean:
	rm -rf $(BUILD_DIR)

# Run tests for clox.
TEST_PATTERN?="test/**/*.lox"
test_clox: clox
	python -m tooling.test_runner.cli ./clox $(TEST_PATTERN)

# Run tests for tooling.
test_tooling:
	poetry run pytest tooling/test

# Run all tests for clox and tooling.
test: test_clox test_tooling

.PHONY: clean clox debug test
