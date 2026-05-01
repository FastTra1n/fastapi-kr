from confest import client

def test_register_user_success(client):
    response = client.post("/users", json={
        "username": "good_username",
        "password": "good_password"
    })

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "good_username"
    assert "password" not in data

def test_register_user_duplicate(client):
    client.post("/users", json={
        "username": "good_username",
        "password": "good_password"
    })
    response = client.post("/users", json={
        "username": "good_username",
        "password": "good_password"
    })

    assert response.status_code == 400
    assert response.json() == {"detail": "User with the same username already exists."}


def test_get_user_information_success(client):
    create_response = client.post("/users", json={
        "username": "another_good_username",
        "password": "another_good_password"
    })
    user_id = create_response.json()["id"]
    response = client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "another_good_username"

def test_get_user_information_not_found(client):
    response = client.get(f"/users/random_id")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "User with this id not found."}


def test_delete_user_success(client):
    create_response = client.post("/users", json={
        "username": "one_more_good_username",
        "password": "one_more_good_password"
    })
    user_id = create_response.json()["id"]
    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 204
    assert response.text == ''
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_delete_user_not_found(client):
    response = client.delete(f"/users/random_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "User with this id not found."}