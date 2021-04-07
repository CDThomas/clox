#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"

// OpCode is the kind of instruction.
typedef enum {
  OP_RETURN, // return from the current function
} OpCode;

// A chunk is a sequence of bytecode. Bytecode is the instructions given to the VM.
typedef struct {
  int count; // the number of allocated entries that are in use
  int capacity; // the number of elements allocated for the array
  uint8_t* code; // dynamic array of bytes
} Chunk;

void initChunk(Chunk* chunk);
void freeChunk(Chunk* chunk);
void writeChunk(Chunk* chunk, uint8_t byte);

#endif
