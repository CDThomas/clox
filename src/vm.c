#include <stdio.h>

#include "common.h"
#include "debug.h"
#include "vm.h"

// Single, global VM object. Would prob want to pass around a pointer to the VM in an actual language.
VM vm;

void initVM() {

}

void freeVM() {

}

static InterpretResult run() {
// Reads the byte currently pointed at by ip and then advances the instruction pointer.
#define READ_BYTE() (*vm.ip++)
// Reads the next byte from the bytecode, treats the resulting number as an index, and
// looks up the corresponding Value in the chunk's constant table.
#define READ_CONSTANT() (vm.chunk->constants.values[READ_BYTE()])

  for(;;) {
#ifdef DEBUG_TRACE_EXECUTION
    // convert ip back to relative offset from beginning of bytecode and then disassemble
    // the instruction that begins at that byte.
    disassembleInstruction(vm.chunk, (int)(vm.ip - vm.chunk->code));
#endif

    uint8_t instruction;
    switch (instruction = READ_BYTE()) {
      case OP_CONSTANT: {
        Value constant = READ_CONSTANT();
        printValue(constant);
        printf("\n");
        break;
      }
      case OP_RETURN: {
        return INTERPRET_OK;
      }
    }
  }

#undef READ_BYTE
#undef READ_CONSTANT
}

InterpretResult interpret(Chunk* chunk) {
  vm.chunk = chunk;
  vm.ip = vm.chunk->code;
  return run();
}
