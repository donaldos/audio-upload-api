# tests/test_smoke.py - test mode
def test_app_object_exists():
    from APP.main import app
    assert app is not None