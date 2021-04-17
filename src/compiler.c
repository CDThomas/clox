#include <stdio.h>
#include <stdlib.h>

#include "common.h"
#include "compiler.h"
#include "scanner.h"

typedef struct {
  Token current;
  Token previous;
  bool hadError;
  bool panicMode;
} Parser;

Parser parser;

static void errorAt(Token* token, const char* message) {
  if (parser.panicMode) return;
  parser.panicMode = true;

  fprintf(stderr, "[line %d] Error", token->line);

  if (token->type == TOKEN_EOF) {
    fprintf(stderr, " at end");
  } else if (token->type == TOKEN_ERROR) {
    // Nothing.
  } else {
    fprintf(stderr, " at '%.*s'", token->length, token->start);
  }

  fprintf(stderr, ": %s\n", message);
  parser.hadError = true;
}

static void error(const char* message) {
  errorAt(&parser.previous, message);
}

static void errorAtCurrent(const char* message) {
  errorAt(&parser.current, message);
}

static void advance() {
  parser.previous = parser.current;

  for (;;) {
    parser.current = scanToken();
    if (parser.current.type != TOKEN_ERROR) break;

    // clox's scanner doesn't report lexical errors (it only emits error tokens),
    // so we report the error here while parsing instead.
    errorAtCurrent(parser.current.start);
  }
}

// Validates that a token has an expected type and advances. If the token doesn't have
// the expected type, report an error.
static void consume(TokenType type, const char* message) {
  if (parser.current.type == type) {
    advance();
    return;
  }

  errorAtCurrent(message);
}

bool compile(const char* source, Chunk* chunk) {
  initScanner(source);

  parser.hadError = false;
  parser.panicMode = false;

  advance();
  // For now we only compile a single expression (until we add statement support).
  expression();
  // Verify that we're at the end of the file.
  consume(TOKEN_EOF, "Expect end of expression.");
  return !parser.hadError;
}
