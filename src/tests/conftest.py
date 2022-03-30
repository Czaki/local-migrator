import pytest

@pytest.fixture
def clean_register():
    from nme._json_hooks import REGISTER

    old_dict = REGISTER._data_dkt
    REGISTER._data_dkt = {}
    yield
    REGISTER._data_dkt = old_dict
