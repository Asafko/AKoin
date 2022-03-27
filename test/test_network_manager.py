import mock
import pytest

from akoin_blockchain.network_manager import NetworkManager
from akoin_blockchain.helper_functions import generate_random_string 
from akoin_blockchain.constants import HEADERSIZE, MAX_MESSAGE_SIZE

MESSAGE_LENGTH = 128

def make_mock_socket(message):
    class Buffer:
        def __init__(self):
            self.serialized_message = serialize_message(message)
            self.max_len = len(self.serialized_message) + HEADERSIZE
            self.len_sent = 0
            
        def recv(self, size):
            part = self.serialized_message[self.len_sent: self.len_sent + size]
            self.len_sent += size
            return part 
            
    mock_socket = mock.Mock()
    buffer = Buffer()
    mock_socket.recv = buffer.recv
    return mock_socket

def serialize_message(message):
    data = {'message': message}
    return NetworkManager.serialize_message(data)

def get_message_parts(msg):
    return msg[:HEADERSIZE], msg[HEADERSIZE:]

def validate_serialized_message(message, header, deserialized_message):
    assert int(header) > MESSAGE_LENGTH  #  no need to trim
    assert 'message' in deserialized_message
    assert deserialized_message['message'] == message
    
def test_serialization():
    message = generate_random_string(MESSAGE_LENGTH)
    assert len(message) == MESSAGE_LENGTH
    serialized_message = serialize_message(message)
    header, serialized_body = get_message_parts(serialized_message)
    deserialized_message = NetworkManager.deserialize(serialized_body)
    validate_serialized_message(message, header, deserialized_message)
    
def test_parse_message_buffer_success():
    message = generate_random_string(MESSAGE_LENGTH)
    assert len(message) == MESSAGE_LENGTH
    mock_socket = make_mock_socket(message)
    
    serialized_message_from_buffer = NetworkManager.parse_message_buffer(mock_socket)
    deserialized_message = NetworkManager.deserialize(serialized_message_from_buffer)
    assert deserialized_message['message'] == message
    
def test_parse_message_buffer_failure():
    message = generate_random_string(MAX_MESSAGE_SIZE)  
    #  would socket buffer would contain a message exceeding max message size
    mock_socket = make_mock_socket(message)
    with pytest.raises(Exception):
        NetworkManager.parse_message_buffer(mock_socket)
