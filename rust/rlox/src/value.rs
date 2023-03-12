use std::fmt;

#[derive(Debug)]
pub enum Value {
    Float(f64),
}

impl From<f64> for Value {
    fn from(f: f64) -> Value {
        Value::Float(f)
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Value::Float(val) => write!(f, "{}", val),
        }
    }
}
