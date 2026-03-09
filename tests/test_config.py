# Tests for CalculatorConfig

import pytest
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


# CalculatorConfig Tests

class TestCalculatorConfig:

    def test_default_creation(self):
        config = CalculatorConfig()
        assert config.max_history_size == 1000
        assert config.auto_save == True
        assert config.precision == 10
        assert config.default_encoding == 'utf-8'

    def test_explicit_values(self):
        config = CalculatorConfig(
            max_history_size=500,
            auto_save=False,
            precision=5,
            max_input_value=Decimal('1000'),
            default_encoding='ascii'
        )
        assert config.max_history_size == 500
        assert config.auto_save == False
        assert config.precision == 5
        assert config.max_input_value == Decimal('1000')
        assert config.default_encoding == 'ascii'

    def test_default_dir(self):
        config = CalculatorConfig()
        assert config.base_dir.is_absolute()

    def test_explicit_base_dir(self, tmp_path):
        config = CalculatorConfig(base_dir=tmp_path)
        assert config.base_dir == tmp_path.resolve()

    def test_history_dir_property(self):
        config = CalculatorConfig()
        assert config.history_dir == (config.base_dir / 'history').resolve()

    def test_log_dir_property(self):
        config = CalculatorConfig()
        assert config.log_dir == (config.base_dir / 'logs').resolve()

    def test_history_file_property(self):
        config = CalculatorConfig()
        assert config.history_file == (config.history_dir / 'calculator_history.csv').resolve()

    def test_log_file_property(self):
        config = CalculatorConfig()
        assert config.log_file == (config.log_dir / 'calculator.log').resolve()

    def test_validate_passes_with_valid_config(self):
        config = CalculatorConfig()
        config.validate()  # should not raise

    def test_validate_rejects_zero_history_size(self):
        config = CalculatorConfig(max_history_size=1)
        config.max_history_size = 0
        with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
            config.validate()

    def test_validate_rejects_zero_precision(self):
        config = CalculatorConfig()
        config.precision = 0
        with pytest.raises(ConfigurationError, match="precision must be positive"):
            config.validate()

    def test_validate_rejects_zero_max_input_value(self):
        config = CalculatorConfig()
        config.max_input_value = Decimal('0')
        with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
            config.validate()

    def test_auto_save_false(self):
        config = CalculatorConfig(auto_save=False)
        assert config.auto_save == False

    def test_precision_zero_explicit(self):
        config = CalculatorConfig(precision=1)
        config.precision = 0
        with pytest.raises(ConfigurationError):
            config.validate()