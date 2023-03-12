use rlox::chunk::{Chunk, OpCode};

fn main() {
    let mut chunk = Chunk::new();

    chunk.write_byte(OpCode::OpReturn);

    chunk.disassemble("test chunk");
}
