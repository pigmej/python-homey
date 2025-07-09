"""Tests for SystemManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from homey.managers.system import SystemManager
from homey.models.system import SystemConfig
from homey.exceptions import HomeyAPIError


class TestSystemManager:
    """Test cases for SystemManager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = MagicMock()
        client.base_url = "http://test-homey.local"
        client.token = "test-token"
        return client

    @pytest.fixture
    def system_manager(self, mock_client):
        """Create a SystemManager instance with mock client."""
        return SystemManager(mock_client)

    @pytest.mark.asyncio
    async def test_get_location_success(self, system_manager):
        """Test successful location retrieval."""
        expected_location = {"latitude": 52.3676, "longitude": 4.9041}

        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_location

            result = await system_manager.get_location()

            assert result == expected_location
            mock_get.assert_called_once_with("/manager/geolocation/option/location")

    @pytest.mark.asyncio
    async def test_get_address_success(self, system_manager):
        """Test successful address retrieval."""
        expected_address = "123 Main St, City, Country"

        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"address": expected_address}

            result = await system_manager.get_address()

            assert result == expected_address
            mock_get.assert_called_once_with("/manager/geolocation/option/address")

    @pytest.mark.asyncio
    async def test_get_address_string_response(self, system_manager):
        """Test address retrieval with string response."""
        expected_address = "123 Main St, City, Country"

        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_address

            result = await system_manager.get_address()

            assert result == expected_address

    @pytest.mark.asyncio
    async def test_get_language_success(self, system_manager):
        """Test successful language retrieval."""
        expected_language = "en"

        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"language": expected_language}

            result = await system_manager.get_language()

            assert result == expected_language
            mock_get.assert_called_once_with("/manager/i18n/option/language")

    @pytest.mark.asyncio
    async def test_get_units_success(self, system_manager):
        """Test successful units retrieval."""
        expected_units = "metric"

        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"units": expected_units}

            result = await system_manager.get_units()

            assert result == expected_units
            mock_get.assert_called_once_with("/manager/i18n/option/units")

    @pytest.mark.asyncio
    async def test_get_system_config_success(self, system_manager):
        """Test successful system configuration retrieval."""
        location_data = {"latitude": 52.3676, "longitude": 4.9041}
        address_data = "123 Main St, City, Country"
        language_data = "en"
        units_data = "metric"

        with patch.object(
            system_manager, "_get_location", new_callable=AsyncMock
        ) as mock_location, patch.object(
            system_manager, "_get_address", new_callable=AsyncMock
        ) as mock_address, patch.object(
            system_manager, "_get_language", new_callable=AsyncMock
        ) as mock_language, patch.object(
            system_manager, "_get_units", new_callable=AsyncMock
        ) as mock_units:
            mock_location.return_value = location_data
            mock_address.return_value = address_data
            mock_language.return_value = language_data
            mock_units.return_value = units_data

            result = await system_manager.get_system_config()

            assert isinstance(result, SystemConfig)
            assert result.location == location_data
            assert result.address == address_data
            assert result.language == language_data
            assert result.units == units_data

    @pytest.mark.asyncio
    async def test_set_location_success(self, system_manager):
        """Test successful location setting."""
        location_data = {"latitude": 52.3676, "longitude": 4.9041}

        with patch.object(system_manager, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await system_manager.set_location(location_data)

            assert result is True
            mock_put.assert_called_once_with(
                "/manager/geolocation/option/location", data=location_data
            )

    @pytest.mark.asyncio
    async def test_set_address_success(self, system_manager):
        """Test successful address setting."""
        address = "123 Main St, City, Country"

        with patch.object(system_manager, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await system_manager.set_address(address)

            assert result is True
            mock_put.assert_called_once_with(
                "/manager/geolocation/option/address", data={"address": address}
            )

    @pytest.mark.asyncio
    async def test_set_language_success(self, system_manager):
        """Test successful language setting."""
        language = "en"

        with patch.object(system_manager, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await system_manager.set_language(language)

            assert result is True
            mock_put.assert_called_once_with(
                "/manager/i18n/option/language", data={"language": language}
            )

    @pytest.mark.asyncio
    async def test_set_units_success(self, system_manager):
        """Test successful units setting."""
        units = "metric"

        with patch.object(system_manager, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await system_manager.set_units(units)

            assert result is True
            mock_put.assert_called_once_with(
                "/manager/i18n/option/units", data={"units": units}
            )

    @pytest.mark.asyncio
    async def test_update_system_config_success(self, system_manager):
        """Test successful system configuration update."""
        config = SystemConfig(
            location={"latitude": 52.3676, "longitude": 4.9041},
            address="123 Main St, City, Country",
            language="en",
            units="metric",
        )

        with patch.object(
            system_manager, "set_location", new_callable=AsyncMock
        ) as mock_set_location, patch.object(
            system_manager, "set_address", new_callable=AsyncMock
        ) as mock_set_address, patch.object(
            system_manager, "set_language", new_callable=AsyncMock
        ) as mock_set_language, patch.object(
            system_manager, "set_units", new_callable=AsyncMock
        ) as mock_set_units, patch.object(
            system_manager, "get_system_config", new_callable=AsyncMock
        ) as mock_get_config:
            mock_set_location.return_value = True
            mock_set_address.return_value = True
            mock_set_language.return_value = True
            mock_set_units.return_value = True
            mock_get_config.return_value = config

            result = await system_manager.update_system_config(config)

            assert result == config
            mock_set_location.assert_called_once_with(config.location)
            mock_set_address.assert_called_once_with(config.address)
            mock_set_language.assert_called_once_with(config.language)
            mock_set_units.assert_called_once_with(config.units)
            mock_get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_system_config_partial(self, system_manager):
        """Test partial system configuration update."""
        config = SystemConfig(language="en", units="metric")

        with patch.object(
            system_manager, "set_location", new_callable=AsyncMock
        ) as mock_set_location, patch.object(
            system_manager, "set_address", new_callable=AsyncMock
        ) as mock_set_address, patch.object(
            system_manager, "set_language", new_callable=AsyncMock
        ) as mock_set_language, patch.object(
            system_manager, "set_units", new_callable=AsyncMock
        ) as mock_set_units, patch.object(
            system_manager, "get_system_config", new_callable=AsyncMock
        ) as mock_get_config:
            mock_set_language.return_value = True
            mock_set_units.return_value = True
            mock_get_config.return_value = config

            result = await system_manager.update_system_config(config)

            assert result == config
            mock_set_location.assert_not_called()
            mock_set_address.assert_not_called()
            mock_set_language.assert_called_once_with(config.language)
            mock_set_units.assert_called_once_with(config.units)

    @pytest.mark.asyncio
    async def test_get_location_error(self, system_manager):
        """Test location retrieval error handling."""
        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")

            with pytest.raises(HomeyAPIError) as exc_info:
                await system_manager.get_location()

            assert "Failed to get location" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_address_error(self, system_manager):
        """Test address retrieval error handling."""
        with patch.object(system_manager, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")

            with pytest.raises(HomeyAPIError) as exc_info:
                await system_manager.get_address()

            assert "Failed to get address" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_location_error(self, system_manager):
        """Test location setting error handling."""
        with patch.object(system_manager, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.side_effect = Exception("Network error")

            with pytest.raises(HomeyAPIError) as exc_info:
                await system_manager.set_location(
                    {"latitude": 52.3676, "longitude": 4.9041}
                )

            assert "Failed to set location" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_system_config_error(self, system_manager):
        """Test system configuration retrieval error handling."""
        with patch.object(
            system_manager, "_get_location", new_callable=AsyncMock
        ) as mock_location:
            mock_location.side_effect = Exception("Network error")

            with pytest.raises(HomeyAPIError) as exc_info:
                await system_manager.get_system_config()

            assert "Failed to get system configuration" in str(exc_info.value)


class TestSystemConfig:
    """Test cases for SystemConfig model."""

    def test_system_config_initialization(self):
        """Test SystemConfig initialization."""
        config = SystemConfig(
            location={"latitude": 52.3676, "longitude": 4.9041},
            address="123 Main St, City, Country",
            language="en",
            units="metric",
        )

        assert config.location == {"latitude": 52.3676, "longitude": 4.9041}
        assert config.address == "123 Main St, City, Country"
        assert config.language == "en"
        assert config.units == "metric"

    def test_get_location_coordinates(self):
        """Test location coordinates extraction."""
        config = SystemConfig(location={"latitude": 52.3676, "longitude": 4.9041})

        coords = config.get_location_coordinates()

        assert coords == {"latitude": 52.3676, "longitude": 4.9041}

    def test_get_location_coordinates_none(self):
        """Test location coordinates extraction with no location."""
        config = SystemConfig()

        coords = config.get_location_coordinates()

        assert coords is None

    def test_is_metric(self):
        """Test metric units check."""
        config = SystemConfig(units="metric")

        assert config.is_metric() is True
        assert config.is_imperial() is False

    def test_is_imperial(self):
        """Test imperial units check."""
        config = SystemConfig(units="imperial")

        assert config.is_metric() is False
        assert config.is_imperial() is True

    def test_units_none(self):
        """Test units check with no units set."""
        config = SystemConfig()

        assert config.is_metric() is True  # Default to metric
        assert config.is_imperial() is False

    def test_update_methods(self):
        """Test update methods."""
        config = SystemConfig()

        location = {"latitude": 52.3676, "longitude": 4.9041}
        config.update_location(location)
        assert config.location == location

        address = "123 Main St"
        config.update_address(address)
        assert config.address == address

        language = "en"
        config.update_language(language)
        assert config.language == language

        units = "metric"
        config.update_units(units)
        assert config.units == units

    def test_str_representation(self):
        """Test string representation."""
        config = SystemConfig(language="en", units="metric", address="123 Main St")

        str_repr = str(config)

        assert "SystemConfig" in str_repr
        assert "language=en" in str_repr
        assert "units=metric" in str_repr
        assert "address=123 Main St" in str_repr
