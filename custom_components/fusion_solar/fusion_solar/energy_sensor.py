import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.const import DEVICE_CLASS_ENERGY, UnitOfEnergy

from .const import ATTR_TOTAL_LIFETIME_ENERGY, ATTR_REALTIME_POWER

_LOGGER = logging.getLogger(__name__)


def isfloat(num) -> bool:
    try:
        float(num)
        return True
    except ValueError:
        return False


class FusionSolarEnergySensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarEnergySensor sensors."""

    def __init__(
            self,
            coordinator,
            unique_id,
            name,
            attribute,
            data_name,
            device_info=None
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._name = name
        self._attribute = attribute
        self._data_name = data_name
        self._device_info = device_info

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> float:
        # It seems like Huawei Fusion Solar returns some invalid data for the lifetime energy just before midnight
        # Therefore we validate if the new value is higher than the current value
        if ATTR_TOTAL_LIFETIME_ENERGY == self._attribute:
            # Grab the current data
            entity = self.hass.states.get(self.entity_id)

            if entity is not None:
                current_value = entity.state
                new_value = self.coordinator.data[self._data_name][self._attribute]
                realtime_power = self.coordinator.data[self._data_name][ATTR_REALTIME_POWER]

                if realtime_power == '0.00':
                    _LOGGER.info(
                        f'{self.entity_id}: not producing any power, so not updating to prevent positive glitched.')
                    return float(current_value)

        if self._data_name not in self.coordinator.data:
            return None

        if self._attribute not in self.coordinator.data[self._data_name]:
            return None

        return float(self.coordinator.data[self._data_name][self._attribute])

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        return self.state if self.state else ''

    @property
    def native_unit_of_measurement(self) -> str:
        return self.unit_of_measurement

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarEnergySensorTotalCurrentDay(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentMonth(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentYear(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalLifetime(FusionSolarEnergySensor):
    pass
