""" Nominal Unit test module"""
# from unittest.mock import patch
from datetime import datetime

from homeassistant.setup import async_setup_component

from .commons import *  # pylint: disable=wildcard-import, unused-wildcard-import


async def test_normal_start_one_device(hass: HomeAssistant):
    """A full nominal start of Solar Optimizer"""

    config = {
        "solar_optimizer": {
            "algorithm": {
                "initial_temp": 1000,
                "min_temp": 0.1,
                "cooling_factor": 0.95,
                "max_iteration_number": 1000,
            },
            "devices": [
                {
                    "name": "Equipement A",
                    "entity_id": "input_boolean.fake_device_a",
                    "power_max": 1000,
                    "check_usable_template": "{{ True }}",
                    "duration_min": 0.3,
                    "duration_stop_min": 0.1,
                    "action_mode": "action_call",
                    "activation_service": "input_boolean/turn_on",
                    "deactivation_service": "input_boolean/turn_off",
                    "max_on_time_per_day_min": 10,
                },
                {
                    "name": "Equipement B",
                    "entity_id": "input_boolean.fake_device_b",
                    "power_max": 2000,
                    "power_min": 100,
                    "power_step": 150,
                    "check_usable_template": "{{ False }}",
                    "duration_min": 1,
                    "duration_stop_min": 2,
                    "duration_power_min": 3,
                    "action_mode": "event",
                    "activation_service": "input_boolean/turn_on",
                    "deactivation_service": "input_boolean/turn_off",
                    "convert_power_divide_factor": 6,
                    "change_power_service": "input_number/set_value",
                    "power_entity_id": "input_number.tesla_amps",
                },
            ],
        }
    }

    # Initialiser le composant avec la configuration de test
    assert await async_setup_component(hass, "solar_optimizer", config)

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="TheSolarOptimizer",
        unique_id="uniqueId",
        data={},
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    coordinator: SolarOptimizerCoordinator = hass.data[DOMAIN]["coordinator"]
    assert coordinator is not None

    assert coordinator.devices is not None
    assert len(coordinator.devices) == 2

    #
    # First device tests
    device:ManagedDevice = coordinator.devices[0]
    assert device.name == "Equipement A"
    assert device.is_enabled is True
    assert device.is_active is False
    assert device.is_usable is True
    assert device.is_waiting is False
    assert device.power_max == 1000
    assert device.power_min == -1
    assert device.power_step == 0
    assert device.duration_sec == 18
    assert device.duration_stop_sec == 6
    # duration_power is set to duration_sec in not power mode
    assert device.duration_power_sec == 18
    assert device.entity_id == "input_boolean.fake_device_a"
    assert device.power_entity_id is None
    assert device.current_power == 0
    assert device.requested_power == 0
    assert device.can_change_power is False
    assert device.max_on_time_per_day_sec == 10 * 60

    tz = get_tz(hass) # pylint: disable=invalid-name
    now: datetime = datetime.now(tz=tz)
    assert (device.next_date_available.astimezone(tz) - now).total_seconds() < 1
    assert (device.next_date_available_power.astimezone(tz) - now).total_seconds() < 1

    assert device.convert_power_divide_factor == 1

    #
    # Second device test
    #
    device = coordinator.devices[1]
    assert device.name == "Equipement B"
    assert device.is_enabled is True
    assert device.is_active is False
    assert device.is_usable is False
    assert device.is_waiting is False
    assert device.power_max == 2000
    assert device.power_min == 100
    assert device.power_step == 150
    assert device.duration_sec == 60
    assert device.duration_stop_sec == 120
    # duration_power is set to duration_sec in not power mode
    assert device.duration_power_sec == 180
    assert device.entity_id == "input_boolean.fake_device_b"
    assert device.power_entity_id == "input_number.tesla_amps"
    assert device.current_power == 0
    assert device.requested_power == 0
    assert device.can_change_power is True
    assert device.max_on_time_per_day_sec == 24 * 60 * 60

    tz = get_tz(hass) # pylint: disable=invalid-name
    now: datetime = datetime.now(tz=tz)
    assert (device.next_date_available.astimezone(tz) - now).total_seconds() < 1
    assert (device.next_date_available_power.astimezone(tz) - now).total_seconds() < 1

    assert device.convert_power_divide_factor == 6
