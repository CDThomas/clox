#ifndef clox_vm_h
#define clox_vm_h

#include "chunk.h"
#include "table.h"
#include "value.h"

#define STACK_MAX 256

typedef struct {
  // Pointer to the chunk being executed.
  Chunk* chunk;
  // Instruction pointer - pointer to the instruction that's about to be executed (next byte of code to
  // by used). ip uses a pointer because pointer dereferences are faster than array lookup by index.
  uint8_t* ip;
  Value stack[STACK_MAX];
  // Direct pointer to top of the stack. Points just past the element containing the top value (where the
  // next value to be pushed will go).
  Value* stackTop;
  // Hash table of interned strings
  Table strings;
  // Intrusive linked list of all objects that have been allocated.
  Obj* objects;
} VM;

typedef enum {
  INTERPRET_OK,
  INTERPRET_COMPILE_ERROR,
  INTERPRET_RUNTIME_ERROR
} InterpretResult;

extern VM vm;

void initVM();
void freeVM();
InterpretResult interpret(const char* source);
void push(Value value);
Value pop();

#endif
