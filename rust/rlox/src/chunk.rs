use crate::value::Value;

pub enum OpCode {
    OpConstant,
    OpReturn,
}

impl From<OpCode> for u8 {
    fn from(value: OpCode) -> u8 {
        value as u8
    }
}

impl TryFrom<u8> for OpCode {
    type Error = String;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            value if value == OpCode::OpReturn as u8 => Ok(OpCode::OpReturn),
            value if value == OpCode::OpConstant as u8 => Ok(OpCode::OpConstant),
            _ => Err(format!(
                "Failed to convert u8 to OpCode. No OpCode matches value: {value}"
            )),
        }
    }
}

#[derive(Debug, Default)]
pub struct Chunk {
    pub code: Vec<u8>,
    pub constants: Vec<Value>,
    pub lines: Vec<usize>,
}

impl Chunk {
    pub fn new() -> Self {
        Chunk::default()
    }

    pub fn write_byte(&mut self, byte: impl Into<u8>, line: usize) {
        self.code.push(byte.into());
        self.lines.push(line);
    }

    pub fn disassemble(&self, name: &str) {
        println!("== {name} ==");

        let mut offset = 0;
        while offset < self.code.len() {
            offset = self.disassemble_instruction(offset);
        }
    }

    pub fn add_constant(&mut self, constant: impl Into<Value>) -> usize {
        self.constants.push(constant.into());
        self.constants.len() - 1
    }

    fn disassemble_instruction(&self, offset: usize) -> usize {
        print!("{offset:04} ");

        let line = self.lines[offset];
        if offset > 0 && line == self.lines[offset - 1] {
            print!("   | ");
        } else {
            print!("{line:4} ");
        }

        let instruction: OpCode = self.code[offset]
            .try_into()
            .expect("failed to convert byte to OpCode");

        match instruction {
            OpCode::OpReturn => simple_instruction("OP_RETURN", offset),
            OpCode::OpConstant => constant_instruction("OP_CONSTANT", self, offset),
        }
    }
}

fn simple_instruction(name: &str, offset: usize) -> usize {
    println!("{name}");
    offset + 1
}

fn constant_instruction(name: &str, chunk: &Chunk, offset: usize) -> usize {
    let constant = chunk.code[offset + 1] as usize;
    let value = &chunk.constants[constant];

    println!("{name:<16} {constant:>4} '{value}'");

    offset + 2
}
