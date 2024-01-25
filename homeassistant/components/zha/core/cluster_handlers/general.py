"""General cluster handlers module for Zigbee Home Automation."""
from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any

from zhaquirks.quirk_ids import TUYA_PLUG_ONOFF
import zigpy.exceptions
import zigpy.types as t
import zigpy.zcl
from zigpy.zcl.clusters import general
from zigpy.zcl.foundation import Status

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later

from .. import registries
from ..const import (
    REPORT_CONFIG_ASAP,
    REPORT_CONFIG_BATTERY_SAVE,
    REPORT_CONFIG_DEFAULT,
    REPORT_CONFIG_IMMEDIATE,
    REPORT_CONFIG_MAX_INT,
    REPORT_CONFIG_MIN_INT,
    SIGNAL_ATTR_UPDATED,
    SIGNAL_MOVE_LEVEL,
    SIGNAL_SET_LEVEL,
    SIGNAL_UPDATE_DEVICE,
)
from . import (
    AttrReportConfig,
    ClientClusterHandler,
    ClusterHandler,
    parse_and_log_command,
)
from .helpers import is_hue_motion_sensor

if TYPE_CHECKING:
    from ..endpoint import Endpoint


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Alarms.cluster_id)
class Alarms(ClusterHandler):
    """Alarms cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.AnalogInput.cluster_id)
class AnalogInput(ClusterHandler):
    """Analog Input cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.AnalogInput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.BINDABLE_CLUSTERS.register(general.AnalogOutput.cluster_id)
@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.AnalogOutput.cluster_id)
class AnalogOutput(ClusterHandler):
    """Analog Output cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.AnalogOutput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )
    ZCL_INIT_ATTRS = {
        general.AnalogOutput.AttributeDefs.min_present_value.name: True,
        general.AnalogOutput.AttributeDefs.max_present_value.name: True,
        general.AnalogOutput.AttributeDefs.resolution.name: True,
        general.AnalogOutput.AttributeDefs.relinquish_default.name: True,
        general.AnalogOutput.AttributeDefs.description.name: True,
        general.AnalogOutput.AttributeDefs.engineering_units.name: True,
        general.AnalogOutput.AttributeDefs.application_type.name: True,
    }

    @property
    def present_value(self) -> float | None:
        """Return cached value of present_value."""
        return self.cluster.get(general.AnalogOutput.AttributeDefs.present_value.name)

    @property
    def min_present_value(self) -> float | None:
        """Return cached value of min_present_value."""
        return self.cluster.get(
            general.AnalogOutput.AttributeDefs.min_present_value.name
        )

    @property
    def max_present_value(self) -> float | None:
        """Return cached value of max_present_value."""
        return self.cluster.get(
            general.AnalogOutput.AttributeDefs.max_present_value.name
        )

    @property
    def resolution(self) -> float | None:
        """Return cached value of resolution."""
        return self.cluster.get(general.AnalogOutput.AttributeDefs.resolution.name)

    @property
    def relinquish_default(self) -> float | None:
        """Return cached value of relinquish_default."""
        return self.cluster.get(
            general.AnalogOutput.AttributeDefs.relinquish_default.name
        )

    @property
    def description(self) -> str | None:
        """Return cached value of description."""
        return self.cluster.get(general.AnalogOutput.AttributeDefs.description.name)

    @property
    def engineering_units(self) -> int | None:
        """Return cached value of engineering_units."""
        return self.cluster.get(
            general.AnalogOutput.AttributeDefs.engineering_units.name
        )

    @property
    def application_type(self) -> int | None:
        """Return cached value of application_type."""
        return self.cluster.get(
            general.AnalogOutput.AttributeDefs.application_type.name
        )

    async def async_set_present_value(self, value: float) -> None:
        """Update present_value."""
        await self.write_attributes_safe(
            {general.AnalogOutput.AttributeDefs.present_value.name: value}
        )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.AnalogValue.cluster_id)
class AnalogValue(ClusterHandler):
    """Analog Value cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.AnalogValue.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(
    general.ApplianceControl.cluster_id
)
class ApplianceContorl(ClusterHandler):
    """Appliance Control cluster handler."""


@registries.CLUSTER_HANDLER_ONLY_CLUSTERS.register(general.Basic.cluster_id)
@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Basic.cluster_id)
class BasicClusterHandler(ClusterHandler):
    """Cluster handler to interact with the basic cluster."""

    UNKNOWN = 0
    BATTERY = 3
    BIND: bool = False

    POWER_SOURCES = {
        UNKNOWN: "Unknown",
        1: "Mains (single phase)",
        2: "Mains (3 phase)",
        BATTERY: "Battery",
        4: "DC source",
        5: "Emergency mains constantly powered",
        6: "Emergency mains and transfer switch",
    }

    def __init__(self, cluster: zigpy.zcl.Cluster, endpoint: Endpoint) -> None:
        """Initialize Basic cluster handler."""
        super().__init__(cluster, endpoint)
        if is_hue_motion_sensor(self) and self.cluster.endpoint.endpoint_id == 2:
            self.ZCL_INIT_ATTRS = self.ZCL_INIT_ATTRS.copy()
            self.ZCL_INIT_ATTRS["trigger_indicator"] = True
        elif (
            self.cluster.endpoint.manufacturer == "TexasInstruments"
            and self.cluster.endpoint.model == "ti.router"
        ):
            self.ZCL_INIT_ATTRS = self.ZCL_INIT_ATTRS.copy()
            self.ZCL_INIT_ATTRS["transmit_power"] = True


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.BinaryInput.cluster_id)
class BinaryInput(ClusterHandler):
    """Binary Input cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.BinaryInput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.BinaryOutput.cluster_id)
class BinaryOutput(ClusterHandler):
    """Binary Output cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.BinaryOutput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.BinaryValue.cluster_id)
class BinaryValue(ClusterHandler):
    """Binary Value cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.BinaryValue.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Commissioning.cluster_id)
class Commissioning(ClusterHandler):
    """Commissioning cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(
    general.DeviceTemperature.cluster_id
)
class DeviceTemperature(ClusterHandler):
    """Device Temperature cluster handler."""

    REPORT_CONFIG = (
        {
            "attr": general.DeviceTemperature.AttributeDefs.current_temperature.name,
            "config": (REPORT_CONFIG_MIN_INT, REPORT_CONFIG_MAX_INT, 50),
        },
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.GreenPowerProxy.cluster_id)
class GreenPowerProxy(ClusterHandler):
    """Green Power Proxy cluster handler."""

    BIND: bool = False


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Groups.cluster_id)
class Groups(ClusterHandler):
    """Groups cluster handler."""

    BIND: bool = False


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Identify.cluster_id)
class Identify(ClusterHandler):
    """Identify cluster handler."""

    BIND: bool = False

    @callback
    def cluster_command(self, tsn, command_id, args):
        """Handle commands received to this cluster."""
        cmd = parse_and_log_command(self, tsn, command_id, args)

        if cmd == general.Identify.ServerCommandDefs.trigger_effect.name:
            self.async_send_signal(f"{self.unique_id}_{cmd}", args[0])


@registries.CLIENT_CLUSTER_HANDLER_REGISTRY.register(general.LevelControl.cluster_id)
class LevelControlClientClusterHandler(ClientClusterHandler):
    """LevelControl client cluster."""


@registries.BINDABLE_CLUSTERS.register(general.LevelControl.cluster_id)
@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.LevelControl.cluster_id)
class LevelControlClusterHandler(ClusterHandler):
    """Cluster handler for the LevelControl Zigbee cluster."""

    CURRENT_LEVEL = 0
    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.LevelControl.AttributeDefs.current_level.name,
            config=REPORT_CONFIG_ASAP,
        ),
    )
    ZCL_INIT_ATTRS = {
        general.LevelControl.AttributeDefs.on_off_transition_time.name: True,
        general.LevelControl.AttributeDefs.on_level.name: True,
        general.LevelControl.AttributeDefs.on_transition_time.name: True,
        general.LevelControl.AttributeDefs.off_transition_time.name: True,
        general.LevelControl.AttributeDefs.default_move_rate.name: True,
        general.LevelControl.AttributeDefs.start_up_current_level.name: True,
    }

    @property
    def current_level(self) -> int | None:
        """Return cached value of the current_level attribute."""
        return self.cluster.get(general.LevelControl.AttributeDefs.current_level.name)

    @callback
    def cluster_command(self, tsn, command_id, args):
        """Handle commands received to this cluster."""
        cmd = parse_and_log_command(self, tsn, command_id, args)

        if cmd in (
            general.LevelControl.ServerCommandDefs.move_to_level.name,
            general.LevelControl.ServerCommandDefs.move_to_level_with_on_off.name,
        ):
            self.dispatch_level_change(SIGNAL_SET_LEVEL, args[0])
        elif cmd in (
            general.LevelControl.ServerCommandDefs.move.name,
            general.LevelControl.ServerCommandDefs.move_with_on_off.name,
        ):
            # We should dim slowly -- for now, just step once
            rate = args[1]
            if args[0] == 0xFF:
                rate = 10  # Should read default move rate
            self.dispatch_level_change(SIGNAL_MOVE_LEVEL, -rate if args[0] else rate)
        elif cmd in (
            general.LevelControl.ServerCommandDefs.step.name,
            general.LevelControl.ServerCommandDefs.step_with_on_off.name,
        ):
            # Step (technically may change on/off)
            self.dispatch_level_change(
                SIGNAL_MOVE_LEVEL, -args[1] if args[0] else args[1]
            )

    @callback
    def attribute_updated(self, attrid: int, value: Any, _: Any) -> None:
        """Handle attribute updates on this cluster."""
        self.debug("received attribute: %s update with value: %s", attrid, value)
        if attrid == self.CURRENT_LEVEL:
            self.dispatch_level_change(SIGNAL_SET_LEVEL, value)

    def dispatch_level_change(self, command, level):
        """Dispatch level change."""
        self.async_send_signal(f"{self.unique_id}_{command}", level)


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.MultistateInput.cluster_id)
class MultistateInput(ClusterHandler):
    """Multistate Input cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.MultistateInput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(
    general.MultistateOutput.cluster_id
)
class MultistateOutput(ClusterHandler):
    """Multistate Output cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.MultistateOutput.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.MultistateValue.cluster_id)
class MultistateValue(ClusterHandler):
    """Multistate Value cluster handler."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.MultistateValue.AttributeDefs.present_value.name,
            config=REPORT_CONFIG_DEFAULT,
        ),
    )


@registries.CLIENT_CLUSTER_HANDLER_REGISTRY.register(general.OnOff.cluster_id)
class OnOffClientClusterHandler(ClientClusterHandler):
    """OnOff client cluster handler."""


@registries.BINDABLE_CLUSTERS.register(general.OnOff.cluster_id)
@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.OnOff.cluster_id)
class OnOffClusterHandler(ClusterHandler):
    """Cluster handler for the OnOff Zigbee cluster."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.OnOff.AttributeDefs.on_off.name, config=REPORT_CONFIG_IMMEDIATE
        ),
    )
    ZCL_INIT_ATTRS = {
        general.OnOff.AttributeDefs.start_up_on_off.name: True,
    }

    def __init__(self, cluster: zigpy.zcl.Cluster, endpoint: Endpoint) -> None:
        """Initialize OnOffClusterHandler."""
        super().__init__(cluster, endpoint)
        self._off_listener = None

        if endpoint.device.quirk_id == TUYA_PLUG_ONOFF:
            self.ZCL_INIT_ATTRS = self.ZCL_INIT_ATTRS.copy()
            self.ZCL_INIT_ATTRS["backlight_mode"] = True
            self.ZCL_INIT_ATTRS["power_on_state"] = True
            self.ZCL_INIT_ATTRS["child_lock"] = True

    @classmethod
    def matches(cls, cluster: zigpy.zcl.Cluster, endpoint: Endpoint) -> bool:
        """Filter the cluster match for specific devices."""
        return not (
            cluster.endpoint.device.manufacturer == "Konke"
            and cluster.endpoint.device.model
            in ("3AFE280100510001", "3AFE170100510001")
        )

    @property
    def on_off(self) -> bool | None:
        """Return cached value of on/off attribute."""
        return self.cluster.get(general.OnOff.AttributeDefs.on_off.name)

    async def turn_on(self) -> None:
        """Turn the on off cluster on."""
        result = await self.on()
        if result[1] is not Status.SUCCESS:
            raise HomeAssistantError(f"Failed to turn on: {result[1]}")
        self.cluster.update_attribute(
            general.OnOff.AttributeDefs.on_off.id, t.Bool.true
        )

    async def turn_off(self) -> None:
        """Turn the on off cluster off."""
        result = await self.off()
        if result[1] is not Status.SUCCESS:
            raise HomeAssistantError(f"Failed to turn off: {result[1]}")
        self.cluster.update_attribute(
            general.OnOff.AttributeDefs.on_off.id, t.Bool.false
        )

    @callback
    def cluster_command(self, tsn, command_id, args):
        """Handle commands received to this cluster."""
        cmd = parse_and_log_command(self, tsn, command_id, args)

        if cmd in (
            general.OnOff.ServerCommandDefs.off.name,
            general.OnOff.ServerCommandDefs.off_with_effect.name,
        ):
            self.cluster.update_attribute(
                general.OnOff.AttributeDefs.on_off.id, t.Bool.false
            )
        elif cmd in (
            general.OnOff.ServerCommandDefs.on.name,
            general.OnOff.ServerCommandDefs.on_with_recall_global_scene.name,
        ):
            self.cluster.update_attribute(
                general.OnOff.AttributeDefs.on_off.id, t.Bool.true
            )
        elif cmd == general.OnOff.ServerCommandDefs.on_with_timed_off.name:
            should_accept = args[0]
            on_time = args[1]
            # 0 is always accept 1 is only accept when already on
            if should_accept == 0 or (should_accept == 1 and bool(self.on_off)):
                if self._off_listener is not None:
                    self._off_listener()
                    self._off_listener = None
                self.cluster.update_attribute(
                    general.OnOff.AttributeDefs.on_off.id, t.Bool.true
                )
                if on_time > 0:
                    self._off_listener = async_call_later(
                        self._endpoint.device.hass,
                        (on_time / 10),  # value is in 10ths of a second
                        self.set_to_off,
                    )
        elif cmd == "toggle":
            self.cluster.update_attribute(
                general.OnOff.AttributeDefs.on_off.id, not bool(self.on_off)
            )

    @callback
    def set_to_off(self, *_):
        """Set the state to off."""
        self._off_listener = None
        self.cluster.update_attribute(
            general.OnOff.AttributeDefs.on_off.id, t.Bool.false
        )

    @callback
    def attribute_updated(self, attrid: int, value: Any, _: Any) -> None:
        """Handle attribute updates on this cluster."""
        if attrid == general.OnOff.AttributeDefs.on_off.id:
            self.async_send_signal(
                f"{self.unique_id}_{SIGNAL_ATTR_UPDATED}",
                attrid,
                general.OnOff.AttributeDefs.on_off.name,
                value,
            )

    async def async_update(self):
        """Initialize cluster handler."""
        if self.cluster.is_client:
            return
        from_cache = not self._endpoint.device.is_mains_powered
        self.debug("attempting to update onoff state - from cache: %s", from_cache)
        await self.get_attribute_value(
            general.OnOff.AttributeDefs.on_off.id, from_cache=from_cache
        )
        await super().async_update()


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(
    general.OnOffConfiguration.cluster_id
)
class OnOffConfiguration(ClusterHandler):
    """OnOff Configuration cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Ota.cluster_id)
@registries.CLIENT_CLUSTER_HANDLER_REGISTRY.register(general.Ota.cluster_id)
class Ota(ClientClusterHandler):
    """OTA cluster handler."""

    BIND: bool = False

    @callback
    def cluster_command(
        self, tsn: int, command_id: int, args: list[Any] | None
    ) -> None:
        """Handle OTA commands."""
        if command_id in self.cluster.server_commands:
            cmd_name = self.cluster.server_commands[command_id].name
        else:
            cmd_name = command_id

        signal_id = self._endpoint.unique_id.split("-")[0]
        if cmd_name == "query_next_image":
            assert args
            self.async_send_signal(SIGNAL_UPDATE_DEVICE.format(signal_id), args[3])


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Partition.cluster_id)
class Partition(ClusterHandler):
    """Partition cluster handler."""


@registries.CLUSTER_HANDLER_ONLY_CLUSTERS.register(general.PollControl.cluster_id)
@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.PollControl.cluster_id)
class PollControl(ClusterHandler):
    """Poll Control cluster handler."""

    CHECKIN_INTERVAL = 55 * 60 * 4  # 55min
    CHECKIN_FAST_POLL_TIMEOUT = 2 * 4  # 2s
    LONG_POLL = 6 * 4  # 6s
    _IGNORED_MANUFACTURER_ID = {
        4476,
    }  # IKEA

    async def async_configure_cluster_handler_specific(self) -> None:
        """Configure cluster handler: set check-in interval."""
        await self.write_attributes_safe(
            {
                general.PollControl.AttributeDefs.checkin_interval.name: self.CHECKIN_INTERVAL
            }
        )

    @callback
    def cluster_command(
        self, tsn: int, command_id: int, args: list[Any] | None
    ) -> None:
        """Handle commands received to this cluster."""
        if command_id in self.cluster.client_commands:
            cmd_name = self.cluster.client_commands[command_id].name
        else:
            cmd_name = command_id

        self.debug("Received %s tsn command '%s': %s", tsn, cmd_name, args)
        self.zha_send_event(cmd_name, args)
        if cmd_name == general.PollControl.ClientCommandDefs.checkin.name:
            self.cluster.create_catching_task(self.check_in_response(tsn))

    async def check_in_response(self, tsn: int) -> None:
        """Respond to checkin command."""
        await self.checkin_response(True, self.CHECKIN_FAST_POLL_TIMEOUT, tsn=tsn)
        if self._endpoint.device.manufacturer_code not in self._IGNORED_MANUFACTURER_ID:
            await self.set_long_poll_interval(self.LONG_POLL)
        await self.fast_poll_stop()

    @callback
    def skip_manufacturer_id(self, manufacturer_code: int) -> None:
        """Block a specific manufacturer id from changing default polling."""
        self._IGNORED_MANUFACTURER_ID.add(manufacturer_code)


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(
    general.PowerConfiguration.cluster_id
)
class PowerConfigurationClusterHandler(ClusterHandler):
    """Cluster handler for the zigbee power configuration cluster."""

    REPORT_CONFIG = (
        AttrReportConfig(
            attr=general.PowerConfiguration.AttributeDefs.battery_voltage.name,
            config=REPORT_CONFIG_BATTERY_SAVE,
        ),
        AttrReportConfig(
            attr=general.PowerConfiguration.AttributeDefs.battery_percentage_remaining.name,
            config=REPORT_CONFIG_BATTERY_SAVE,
        ),
    )

    def async_initialize_cluster_handler_specific(self, from_cache: bool) -> Coroutine:
        """Initialize cluster handler specific attrs."""
        attributes = [
            general.PowerConfiguration.AttributeDefs.battery_size.name,
            general.PowerConfiguration.AttributeDefs.battery_quantity.name,
        ]
        return self.get_attributes(
            attributes, from_cache=from_cache, only_cache=from_cache
        )


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.PowerProfile.cluster_id)
class PowerProfile(ClusterHandler):
    """Power Profile cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.RSSILocation.cluster_id)
class RSSILocation(ClusterHandler):
    """RSSI Location cluster handler."""


@registries.CLIENT_CLUSTER_HANDLER_REGISTRY.register(general.Scenes.cluster_id)
class ScenesClientClusterHandler(ClientClusterHandler):
    """Scenes cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Scenes.cluster_id)
class Scenes(ClusterHandler):
    """Scenes cluster handler."""


@registries.ZIGBEE_CLUSTER_HANDLER_REGISTRY.register(general.Time.cluster_id)
class Time(ClusterHandler):
    """Time cluster handler."""
