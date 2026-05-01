async def test_register_user_success(async_client, fake_user_data):
    response = await async_client.post("/users", json=fake_user_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == fake_user_data["username"]
    assert "password" not in data

async def test_register_user_duplicate(async_client, fake_user_data):
    await async_client.post("/users", json=fake_user_data)
    response = await async_client.post("/users", json=fake_user_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "User with the same username already exists."}


async def test_get_user_information_success(async_client, fake_user_data):
    create_response = await async_client.post("/users", json=fake_user_data)
    user_id = create_response.json()["id"]
    response = await async_client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == fake_user_data["username"]

async def test_get_user_information_not_found(async_client):
    response = await async_client.get(f"/users/random_id")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "User with this id not found."}


async def test_delete_user_success(async_client, fake_user_data):
    create_response = await async_client.post("/users", json=fake_user_data)
    user_id = create_response.json()["id"]
    response = await async_client.delete(f"/users/{user_id}")

    assert response.status_code == 204
    assert response.text == ''
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

async def test_delete_user_not_found(async_client):
    response = await async_client.delete(f"/users/random_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "User with this id not found."}

async def test_delete_user_twice(async_client, fake_user_data):
    create_response = await async_client.post("/users", json=fake_user_data)
    user_id = create_response.json()["id"]
    await async_client.delete(f"/users/{user_id}")
    response = await async_client.delete(f"/users/{user_id}")

    assert response.status_code == 404