use rlox::chunk::{Chunk, OpCode};

fn main() {
    let mut chunk = Chunk::new();

    let constant = chunk.add_constant(1.2);
    chunk.write_byte(OpCode::OpConstant, 123);
    chunk.write_byte(constant as u8, 123);

    chunk.write_byte(OpCode::OpReturn, 123);

    chunk.disassemble("test chunk");
}
