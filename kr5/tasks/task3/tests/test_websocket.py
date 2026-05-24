import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_connect_valid_username():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        data = ws.receive_json()
        assert data == {"type": "join", "room_id": "python", "username": "alice"}

        response = client.get('/rooms/python/users')
        assert response.status_code == 200
        assert response.json() == {"room_id": "python", "users": ["alice"]}

def test_send_and_receive_message():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()

        ws.send_json({"type": "message", "text": "Hello World!"})
        data = ws.receive_json()
        assert data == {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Hello World!"
        }

def test_two_clients_same_room():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1, \
         client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
        ws1.receive_json() # Сначала подключилась alice, => отлавливаем event её подключения.
        ws1.receive_json() # Следом подсоединился bob, => нужно отлавить и этот event.
        ws2.receive_json() # Отлавливаем подключение bob'а.

        ws1.send_json({"type": "message", "text": "Hello everyone!"})

        expected = {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Hello everyone!"
        }
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()
        print(data1, data2)
        assert data1 == expected
        assert data2 == expected

def test_different_rooms():
    with client.websocket_connect("/ws/rooms/roomA?username=alice") as ws1, \
         client.websocket_connect("/ws/rooms/roomB?username=bob") as ws2:
        ws1.receive_json()
        ws2.receive_json()

        ws1.send_json({"type": "message", "text": "This message only for room A."})
        data = ws1.receive_json()
        assert data["room_id"] == "roomA"

        with pytest.raises(TypeError):
            ws2.receive_json(timeout=1)

def test_long_message_error():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()

        msg = "test" * 76 # 304 символа.
        ws.send_json({"type": "message", "text": msg})
        error = ws.receive_json()
        assert error == {"type": "error", "detail": "Message is too long"}

def test_disconnect_removes_user():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()

        response = client.get('/rooms/python/users')
        assert response.json() == {"room_id": "python", "users": ["alice"]}

    response = client.get('/rooms/python/users')
    assert response.json() == {"room_id": "python", "users": []}