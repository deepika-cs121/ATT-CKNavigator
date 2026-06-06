import base64
import logging

log_file = "encoding_logs.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log(message):
    print(message)
    logging.info(message)

def standard_encoding(data: str):
    log(f"Original Data: {data}")
    
    utf8_encoded = data.encode('utf-8')
    log(f"UTF-8 Encoded: {utf8_encoded}")
    
    base64_encoded = base64.b64encode(utf8_encoded)
    log(f"Base64 Encoded: {base64_encoded}")
    
    base64_decoded = base64.b64decode(base64_encoded).decode('utf-8')
    log(f"Base64 Decoded: {base64_decoded}")
    log("----- Standard Encoding Done -----\n")

def custom_encoding(data: str, shift: int = 3):
    log(f"Original Data: {data}")
    
    encoded = ''.join([chr((ord(char) + shift) % 256) for char in data])
    log(f"Custom Encoded (Caesar Shift {shift}): {encoded}")
    
    decoded = ''.join([chr((ord(char) - shift) % 256) for char in encoded])
    log(f"Custom Decoded: {decoded}")
    log("----- Non-Standard Encoding Done -----\n")

if __name__ == "__main__":
    log("=== Starting Encoding Script ===")
    
    user_input = input("Enter the data to encode: ")
    
    standard_encoding(user_input)
    
    try:
        shift_value = int(input("Enter custom shift value for non-standard encoding: ") or 3)
    except ValueError:
        shift_value = 3
    
    custom_encoding(user_input, shift=shift_value)
    
    log("Script Finished")
