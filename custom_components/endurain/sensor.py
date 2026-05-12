from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfMass,
    UnitOfSpeed,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EndurainConfigEntry
from .const import ACTIVITY_TYPE_MAP, DOMAIN
from .coordinator import EndurainCoordinator


@dataclass(frozen=True, kw_only=True)
class EndurainSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    available_fn: Callable[[dict[str, Any]], bool] = lambda d: True


def _last_activity(data: dict) -> dict | None:
    return data.get("last_activity")


def _weight(data: dict) -> dict | None:
    return data.get("latest_weight")


def _steps(data: dict) -> dict | None:
    return data.get("latest_steps")


def _sleep(data: dict) -> dict | None:
    return data.get("latest_sleep")


def _weekly(data: dict) -> dict | None:
    return data.get("weekly_distances")


def _monthly(data: dict) -> dict | None:
    return data.get("monthly_distances")


SENSOR_DESCRIPTIONS: tuple[EndurainSensorEntityDescription, ...] = (
    # ----- Last activity -----
    EndurainSensorEntityDescription(
        key="last_activity_name",
        translation_key="last_activity_name",
        value_fn=lambda d: _last_activity(d) and _last_activity(d).get("name"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_type",
        translation_key="last_activity_type",
        value_fn=lambda d: ACTIVITY_TYPE_MAP.get(
            (_last_activity(d) or {}).get("activity_type"), "Unknown"
        )
        if _last_activity(d)
        else None,
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_distance",
        translation_key="last_activity_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("distance"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_duration",
        translation_key="last_activity_duration",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("total_elapsed_time"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_avg_hr",
        translation_key="last_activity_avg_hr",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("average_hr"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_avg_speed",
        translation_key="last_activity_avg_speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("average_speed"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_elevation_gain",
        translation_key="last_activity_elevation_gain",
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("elevation_gain"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="last_activity_calories",
        translation_key="last_activity_calories",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_last_activity(d) or {}).get("calories"),
        available_fn=lambda d: _last_activity(d) is not None,
    ),
    # ----- Weekly distances -----
    EndurainSensorEntityDescription(
        key="weekly_run_distance",
        translation_key="weekly_run_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_weekly(d) or {}).get("run"),
        available_fn=lambda d: _weekly(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="weekly_bike_distance",
        translation_key="weekly_bike_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_weekly(d) or {}).get("bike"),
        available_fn=lambda d: _weekly(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="weekly_swim_distance",
        translation_key="weekly_swim_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_weekly(d) or {}).get("swim"),
        available_fn=lambda d: _weekly(d) is not None,
    ),
    # ----- Monthly distances -----
    EndurainSensorEntityDescription(
        key="monthly_run_distance",
        translation_key="monthly_run_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_monthly(d) or {}).get("run"),
        available_fn=lambda d: _monthly(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="monthly_bike_distance",
        translation_key="monthly_bike_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_monthly(d) or {}).get("bike"),
        available_fn=lambda d: _monthly(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="monthly_swim_distance",
        translation_key="monthly_swim_distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_monthly(d) or {}).get("swim"),
        available_fn=lambda d: _monthly(d) is not None,
    ),
    # ----- Health: weight -----
    EndurainSensorEntityDescription(
        key="weight",
        translation_key="weight",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_weight(d) or {}).get("weight"),
        available_fn=lambda d: _weight(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="body_fat",
        translation_key="body_fat",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_weight(d) or {}).get("body_fat"),
        available_fn=lambda d: _weight(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="muscle_mass",
        translation_key="muscle_mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_weight(d) or {}).get("muscle_mass"),
        available_fn=lambda d: _weight(d) is not None,
    ),
    # ----- Health: steps -----
    EndurainSensorEntityDescription(
        key="steps",
        translation_key="steps",
        native_unit_of_measurement="steps",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (_steps(d) or {}).get("steps"),
        available_fn=lambda d: _steps(d) is not None,
    ),
    # ----- Health: sleep -----
    EndurainSensorEntityDescription(
        key="sleep_total",
        translation_key="sleep_total",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_sleep(d) or {}).get("total_sleep_seconds"),
        available_fn=lambda d: _sleep(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="sleep_score",
        translation_key="sleep_score",
        native_unit_of_measurement="score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_sleep(d) or {}).get("sleep_score_overall"),
        available_fn=lambda d: _sleep(d) is not None,
    ),
    EndurainSensorEntityDescription(
        key="resting_heart_rate",
        translation_key="resting_heart_rate",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (_sleep(d) or {}).get("resting_heart_rate"),
        available_fn=lambda d: _sleep(d) is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EndurainConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EndurainCoordinator = entry.runtime_data
    user = coordinator.data.get("user") or {}
    async_add_entities(
        EndurainSensorEntity(coordinator, description, entry.entry_id, user)
        for description in SENSOR_DESCRIPTIONS
    )


class EndurainSensorEntity(CoordinatorEntity[EndurainCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EndurainCoordinator,
        description: EndurainSensorEntityDescription,
        entry_id: str,
        user: dict,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=user.get("name") or "Endurain",
            manufacturer="Endurain",
            model="Self-hosted",
        )

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.entity_description.available_fn(self.coordinator.data)
        )
