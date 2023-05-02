import pytest


@pytest.fixture()
def clean_register():
    from local_migrator._serialize_hooks import REGISTER

    def clean():
        REGISTER._data_dkt = {}

    old_dict = REGISTER._data_dkt
    clean()
    yield clean
    REGISTER._data_dkt = old_dict
