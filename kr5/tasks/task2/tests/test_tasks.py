def test_create_task_success(client):
    response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Подготовить тесты",
            "description": "Написать интеграционные тесты",
            "status": "todo",
            "priority": 4,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Подготовить тесты"
    assert data["description"] == "Написать интеграционные тесты"
    assert data["status"] == "todo"
    assert data["priority"] == 4
    assert data["owner_id"] == 10

def test_create_task_title_too_short(client):
    response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "По",
            "status": "todo",
            "priority": 4,
        }
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("title" in error["loc"] for error in errors)

def test_create_task_missing_user_id(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Подготовить тесты",
            "description": "Написать интеграционные тесты",
            "status": "todo",
            "priority": 4,
        }
    )

    assert response.status_code == 401
    assert "X-User-Id header is required" in response.text

def test_user_sees_only_own_tasks(client):
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача",
            "description": "Описание задачи",
            "status": "todo",
            "priority": 3,
        }
    )
    client.post(
        "/tasks",
        headers={"X-User-Id": "20"},
        json={
            "title": "Задача другого пользователя",
            "description": "Другое описание",
            "status": "done",
            "priority": 4,
        }
    )
    
    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Задача"
    assert tasks[0]["owner_id"] == 10

def test_filter_tasks(client):
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача №1",
            "description": "Описание задачи",
            "status": "todo",
            "priority": 2
        }
    )
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача №2",
            "description": "Описание задачи",
            "status": "todo",
            "priority": 1
        }
    )
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача №3",
            "description": "Описание задачи",
            "status": "todo",
            "priority": 4
        }
    )

    resp = client.get("/tasks?status=todo", headers={"X-User-Id": "10"})
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 3
    assert all(t["status"] == "todo" for t in tasks)

    resp = client.get("/tasks?min_priority=4", headers={"X-User-Id": "10"})
    tasks = resp.json()
    assert len(tasks) == 1
    assert all(t["priority"] >= 4 for t in tasks)

    resp = client.get("/tasks?status=todo&min_priority=4", headers={"X-User-Id": "10"})
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Задача №3"

def test_update_status_success(client):
    create_resp = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача",
            "description": "Задача для проверки корректности смены статуса",
            "status": "todo",
            "priority": 2
        }
    )
    task_id = create_resp.json()["id"]

    resp = client.patch(
        f"/tasks/{task_id}/status",
        headers={"X-User-Id": "10"},
        json={
            "status": "done"
        }
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"

def test_get_other_task_404(client):
    create_resp = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача",
            "description": "Это задача пользователя с id 10",
            "status": "todo",
            "priority": 1
        }
    )
    task_id = create_resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert resp.status_code == 404

    resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert resp.status_code == 200

    resp = client.get(f"/tasks/999", headers={"X-User-Id": "10"})
    assert resp.status_code == 404

def test_delete_task_success(client):
    create_resp = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача",
            "description": "Простая задачка",
            "status": "todo",
            "priority": 1
        }
    )
    task_id = create_resp.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert resp.status_code == 404

def test_health_endpoint(client):
    resp = client.get("/health")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["env"] == "docker"