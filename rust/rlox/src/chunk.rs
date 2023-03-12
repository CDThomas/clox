pub enum OpCode {
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
            _ => Err(format!(
                "Failed to convert u8 to OpCode. No OpCode matches value: {value}"
            )),
        }
    }
}

#[derive(Debug, Default)]
pub struct Chunk {
    code: Vec<u8>,
}

impl Chunk {
    pub fn new() -> Self {
        Chunk::default()
    }

    pub fn write_byte(&mut self, byte: impl Into<u8>) {
        self.code.push(byte.into());
    }

    pub fn disassemble(&self, name: &str) {
        println!("== {name} ==");

        let mut offset = 0;
        while offset < self.code.len() {
            offset = self.disassemble_instruction(offset);
        }
    }

    fn disassemble_instruction(&self, offset: usize) -> usize {
        print!("{offset:04} ");

        let instruction: OpCode = self.code[offset]
            .try_into()
            .expect("failed to convert byte to OpCode");

        match instruction {
            OpCode::OpReturn => simple_instruction("OP_RETURN", offset),
        }
    }
}

fn simple_instruction(name: &str, offset: usize) -> usize {
    println!("{name}");
    offset + 1
}
