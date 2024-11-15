import requests


# Test the /saveMessage/ endpoint with a valid message
def test_save_message_success():
    response = requests.post('http://127.0.0.1:5001/saveMessage/', data={'message': 'Hello, World!'})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert 'success' in response.text, "Response does not contain 'success'"
    print("test_save_message_success passed.")


# Test the /saveMessage/ endpoint with no content
def test_save_message_no_content():
    response = requests.post('http://127.0.0.1:5001/saveMessage/', data={})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert 'No message provided' in response.text, "Response does not contain 'No message provided'"
    print("test_save_message_no_content passed.")


# Test the /getMessages endpoint
def test_get_messages():
    response = requests.get('http://127.0.0.1:5001/getMessages')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    try:
        messages = response.json()
        assert isinstance(messages, list), f"Expected a list, got {type(messages)}"
        print("test_get_messages passed.")
    except ValueError:
        assert False, "Response is not valid JSON"


# Run the tests
if __name__ == "__main__":
    test_save_message_success()
    test_save_message_no_content()
    test_get_messages()
