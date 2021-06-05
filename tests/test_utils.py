import base64
from os import write, getcwd
from unittest.mock import mock_open, patch

from utils import *

    
def test_convertfile_to_base64str_validfile():
    filename = "path"
    content = b"MOCKED"
    with patch("builtins.open", mock_open(read_data=b"MOCKED"), create=True) as mock_file:
        result = convertfile_to_base64str(filename)
    mock_file.assert_called_once_with(filename, "rb")
    mock_file.return_value.read.assert_called_once()
    assert(result == b64encode(content))

def test_write_base64str_obj_to_file_validtext():
    content = b"Hello World!"
    contentb64 = b64encode(content)
    filename = "FILE"
    with patch("builtins.open", mock_open(), create=True) as mock_file:
        write_base64str_obj_to_file(contentb64, filename)
    mock_file.assert_called_once_with(filename, "wb")
    mock_file.return_value.write.assert_called_once_with(content)