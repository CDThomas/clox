#ifndef clox_vm_h
#define clox_vm_h

#include "chunk.h"

typedef struct {
  // Pointer to the chunk being executed.
  Chunk* chunk;
  // Instruction pointer - pointer to the instruction that's about to be executed (next byte of code to
  // by used). ip uses a pointer because pointer dereferences are faster than array lookup by index.
  uint8_t* ip;
} VM;

typedef enum {
  INTERPRET_OK,
  INTERPRET_COMPILE_ERROR,
  INTERPRET_RUNTIME_ERROR
} InterpretResult;

void initVM();
void freeVM();
InterpretResult interpret(Chunk* chunk);

#endif
