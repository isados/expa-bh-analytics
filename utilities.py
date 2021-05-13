from base64 import b64encode, b64decode

def convertfile_to_base64str(filename: str) -> str :
    try:
        with open(filename, "rb") as file:
            content = file.read()
            return b64encode(content)
    except:
        print("Error reading file")

def write_base64str_obj_to_file(text: str, filename: str) -> None:
    try:
        with open(filename, 'wb') as file:
            file.write(b64decode(text))
    except:
        print("Error in conversion")
    return None
