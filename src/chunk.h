#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"
#include "value.h"

// OpCode is the kind of instruction.
typedef enum {
  OP_CONSTANT, // produces a constant
  OP_RETURN, // return from the current function
} OpCode;

// A chunk is a sequence of bytecode. Bytecode is the instructions given to the VM.
typedef struct {
  int count; // the number of allocated entries that are in use
  int capacity; // the number of elements allocated for the array
  uint8_t* code; // dynamic array of bytes
  int* lines; // dynamic array of line numbers for debugging runtime errors
  ValueArray constants; // dynamic array of constants
} Chunk;

void initChunk(Chunk* chunk);
void freeChunk(Chunk* chunk);
void writeChunk(Chunk* chunk, uint8_t byte, int line);
int addConstant(Chunk* chunk, Value value);

#endif
