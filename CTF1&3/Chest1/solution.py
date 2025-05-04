def atbash_decode(text):
    """Decode a string using the Atbash cipher."""
    decoded = []
    for char in text:
        if 'A' <= char <= 'Z':
            # Uppercase letters: A(65) ↔ Z(90), B(66) ↔ Y(89), etc.
            decoded_char = chr(155 - ord(char))
        elif 'a' <= char <= 'z':
            # Lowercase letters: a(97) ↔ z(122), b(98) ↔ y(121), etc.
            decoded_char = chr(219 - ord(char))
        else:
            # Non-alphabetic characters remain unchanged
            decoded_char = char
        decoded.append(decoded_char)
    return ''.join(decoded)

def main():
    # Read input from 'env.txt'
    
    with open('enc.txt', 'r') as file:
        encoded_text = file.read()
    

    # Decode the text using Atbash
    decoded_text = atbash_decode(encoded_text)

    with open('dec.txt', 'w') as file:
        file.write(decoded_text)

if __name__ == "__main__":
    main()