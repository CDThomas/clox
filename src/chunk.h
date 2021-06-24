#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"
#include "value.h"

// OpCode is the kind of instruction.
typedef enum {
  OP_CONSTANT, // produces a constant. ex: `2.1`
  OP_NIL,
  OP_TRUE,
  OP_FALSE,
  OP_POP,
  OP_GET_GLOBAL,
  OP_DEFINE_GLOBAL,
  OP_EQUAL, // comparison: `1 == 1`
  OP_GREATER, // comparison: `2 > 1`
  OP_LESS, // comparison: `1 < 2`
  OP_ADD, // ex: `1 + 2`
  OP_SUBTRACT, // ex: `12 - 4`
  OP_MULTIPLY, // ex: `34 * 9`
  OP_DIVIDE, // ex: `20 / 2`
  OP_NOT, // unary not: `!true`
  OP_NEGATE, // ex: `-1`
  OP_PRINT, // ex: `print 1`
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
