import src.app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    # Arrange

    # Act
    response = client.get("/activities")
    body = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(body, dict)
    assert "Soccer Team" in body
    soccer = body["Soccer Team"]
    assert "description" in soccer
    assert "schedule" in soccer
    assert "max_participants" in soccer
    assert "participants" in soccer


def test_signup_success_adds_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    new_email = "newstudent@mergington.edu"
    assert new_email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_activity_not_found_returns_404(client):
    # Arrange
    unknown_activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400(client):
    # Arrange
    activity_name = "Soccer Team"
    existing_email = "liam@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_missing_email_returns_422(client):
    # Arrange
    activity_name = "Soccer Team"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_signup_encoded_activity_name_with_space_works(client):
    # Arrange
    encoded_activity = "Soccer%20Team"
    new_email = "encoded@mergington.edu"

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert new_email in app_module.activities["Soccer Team"]["participants"]


def test_unregister_success_removes_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    existing_email = "liam@mergington.edu"
    assert existing_email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {existing_email} from {activity_name}"
    assert existing_email not in app_module.activities[activity_name]["participants"]


def test_unregister_activity_not_found_returns_404(client):
    # Arrange
    unknown_activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{unknown_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_registered_student_returns_404(client):
    # Arrange
    activity_name = "Soccer Team"
    missing_email = "not-registered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
