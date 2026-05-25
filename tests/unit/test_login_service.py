from unittest.mock import MagicMock, patch

from src.services.login_service import login_user


@patch("src.services.login_service.UserAccount")
def test_login_valid_credentials(mock_ua):
    mock_user = MagicMock()
    mock_user.id = 42
    mock_user.status = "active"
    mock_ua.query.filter_by.return_value.first.return_value = mock_user

    with patch("src.services.login_service.check_password_hash", return_value=True):
        user_id, error = login_user("test@gmail.com", "correct_password")

    assert user_id == 42
    assert error is None


@patch("src.services.login_service.UserAccount")
def test_login_wrong_password(mock_ua):
    mock_user = MagicMock()
    mock_user.status = "active"
    mock_ua.query.filter_by.return_value.first.return_value = mock_user

    with patch("src.services.login_service.check_password_hash", return_value=False):
        user_id, error = login_user("test@gmail.com", "wrong_password")

    assert user_id is None
    assert error == "Invalid email or password."


@patch("src.services.login_service.UserAccount")
def test_login_email_not_found(mock_ua):
    mock_ua.query.filter_by.return_value.first.return_value = None

    user_id, error = login_user("nobody@gmail.com", "any_password")

    assert user_id is None
    assert error == "Invalid email or password."


@patch("src.services.login_service.UserAccount")
def test_login_pending_account(mock_ua):
    mock_user = MagicMock()
    mock_user.status = "pending"
    mock_ua.query.filter_by.return_value.first.return_value = mock_user

    with patch("src.services.login_service.check_password_hash", return_value=True):
        user_id, error = login_user("pending@gmail.com", "correct_password")

    assert user_id is None
    assert error == "Invalid email or password."
