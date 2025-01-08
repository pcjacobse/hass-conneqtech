from __future__ import annotations
from typing import Any
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfSoundPressure,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER, get_nested_value, parse_datetime
from .cnt_device import CntDevice
from .conneqtechapi import ConneqtechApi

SENSORS: tuple[SensorEntityDescription, ...] = (
    # payload_state.tracker.metric.bbatp = battery level in percentage
    SensorEntityDescription(
        key="payload_state.tracker.metric.bbatp",
        name="Internal Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.metric.bbatv = battery voltage in volts
    SensorEntityDescription(
        key="payload_state.tracker.metric.bbatv",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.metric.rssi = signal strength in dBm
    SensorEntityDescription(
        key="payload_state.tracker.metric.rssi",
        name="Signal Strength",
        native_unit_of_measurement=UnitOfSoundPressure.DECIBEL,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.metric.temp = temperature in celsius
    SensorEntityDescription(
        key="payload_state.device.metric.bmv",
        name="External Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.loc.sp = speed in km/h
    SensorEntityDescription(
        key="payload_state.tracker.loc.sp",
        name="Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.loc.ang = course in degrees
    SensorEntityDescription(
        key="payload_state.tracker.loc.ang",
        name="Angle",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.tracker.loc.alt = altitude in meters
    SensorEntityDescription(
        key="payload_state.tracker.loc.alt",
        name="Altitude",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # payload_state.dts = last connection date
    SensorEntityDescription(
        key="payload_state.dts",
        name="Last Connection Date",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    # payload_state.tracker.loc.dtg = last location date
    SensorEntityDescription(
        key="payload_state.tracker.loc.dtg",
        name="Last Location Date",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the sensor entities."""
    LOGGER.debug(f"Setting up sensor entities for {DOMAIN}")

    coordinator: ConneqtechApi = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    entities = []
    for _, sensor in enumerate(SENSORS):
        entities.append(ConneqtechSensor(sensor, coordinator))
    async_add_entities(entities, update_before_add=False)


class ConneqtechSensor(CntDevice, SensorEntity):
    def __init__(self, sensor, coordinator: ConneqtechApi) -> None:
        super().__init__(coordinator)
        self.entity_description = sensor
        self._attr_unique_id = f"conneqtech-{
            coordinator.data.imei}-{sensor.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return parse_datetime(get_nested_value(self.coordinator.data.raw, self.entity_description.key))
        return get_nested_value(self.coordinator.data.raw, self.entity_description.key)

    @property
    def available(self) -> bool:
        return self.native_value is not None
