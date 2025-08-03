import pytest
from gui.controllers.config_controller import ConfigController
import json

@pytest.fixture
def config_controller():
    """Fixture for a ConfigController instance."""
    return ConfigController()

def test_initial_dirty_state(config_controller):
    """Test that the dirty flag is initially False."""
    assert not config_controller.is_dirty()

def test_create_default_config_sets_dirty_to_false(config_controller):
    """Test that create_default_config sets the dirty flag to False."""
    # First, make it dirty
    config_controller.set_config({})
    assert config_controller.is_dirty()
    # Then, create default config
    config_controller.create_default_config()
    assert not config_controller.is_dirty()

def test_load_config_sets_dirty_to_false(config_controller, mocker):
    """Test that load_config sets the dirty flag to False."""
    config_controller.set_config({})
    assert config_controller.is_dirty()

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps({})))

    config_controller.load_config("dummy_path")
    assert not config_controller.is_dirty()

def test_save_config_sets_dirty_to_false(config_controller, mocker):
    """Test that save_config sets the dirty flag to False."""
    config_controller.set_config({})
    assert config_controller.is_dirty()

    mocker.patch("os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open())

    config_controller.save_config("dummy_path")
    assert not config_controller.is_dirty()

def test_set_config_makes_dirty(config_controller):
    """Test that set_config sets the dirty flag to True."""
    config_controller.set_config({})
    assert config_controller.is_dirty()

def test_set_data_source_config_makes_dirty(config_controller):
    """Test that set_data_source_config sets the dirty flag to True."""
    config_controller.set_data_source_config({})
    assert config_controller.is_dirty()

def test_set_strategies_config_makes_dirty(config_controller):
    """Test that set_strategies_config sets the dirty flag to True."""
    config_controller.set_strategies_config([])
    assert config_controller.is_dirty()

def test_set_aggregator_config_makes_dirty(config_controller):
    """Test that set_aggregator_config sets the dirty flag to True."""
    config_controller.set_aggregator_config({})
    assert config_controller.is_dirty()

def test_set_report_config_makes_dirty(config_controller):
    """Test that set_report_config sets the dirty flag to True."""
    config_controller.set_report_config({})
    assert config_controller.is_dirty()
