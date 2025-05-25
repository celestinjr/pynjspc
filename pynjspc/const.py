from enum import Enum

# Default parameters for NjsPCClient
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 4200
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_AUTO_RECONNECT = True
DEFAULT_RECONNECT_DELAY = 5.0
DEFAULT_MAX_RECONNECT_ATTEMPTS = 5
DEFAULT_WATCHDOG_TIMEOUT = 60
DEFAULT_FALLBACK_WATCHDOG_SLEEP = 10
DEFAULT_UNKNOWN_EVENTS_LOG = None

class ApiEndpoints(Enum):
    """API endpoint routes for nodejs-PoolController."""
    STATE_ALL = "state/all"
    STATE_STATUS = "state/status"
    CIRCUIT_SETSTATE = "state/circuit/setState"
    CIRCUITGROUP_SETSTATE = "state/circuitGroup/setState"
    LIGHTGROUP_SETSTATE = "state/lightGroup/setState"
    FEATURE_SETSTATE = "state/feature/setState"
    CHLORINATOR_POOL_SETPOINT = "state/chlorinator/poolSetpoint"
    CHLORINATOR_SPA_SETPOINT = "state/chlorinator/spaSetpoint"
    SUPERCHLOR = "state/chlorinator/superChlorinate"
    CIRCUIT_SETTHEME = "state/circuit/setTheme"
    CONFIG_BODY = "config/body"
    HEATMODES = "heatModes"
    CONFIG_CIRCUIT = "config/circuit"
    LIGHTTHEMES = "lightThemes"
    CONFIG_HEATERS = "config/options/heaters"
    CONFIG_CHLORINATOR = "config/chlorinator"
    LIGHTCOMMANDS = "lightCommands"
    LIGHT_RUNCOMMAND = "state/light/runCommand"
    TEMPERATURE_SETPOINT = "state/body/setPoint"
    SET_HEATMODE = "state/body/heatMode"
    CHEM_CONTROLLER_SETPOINT = "state/chemController"
    CONFIG_SCHEDULE = "config/schedule"


class SocketIOEventsInbound(Enum):
    """Socket.IO event names for nodejs-PoolController."""
    CIRCUIT = "circuit"
    BODY = "body"
    TEMPS = "temps"
    CHLORINATOR = "chlorinator"
    PUMP = "pump"
    PUMPEXT = "pumpExt"
    LIGHTGROUP = "lightGroup"
    CIRCUITGROUP = "circuitGroup"
    FEATURE = "feature"
    CONTROLLER = "controller"
    CHEM_CONTROLLER = "chemController"
    FILTER = "filter"
    VIRTUAL_CIRCUIT = "virtualCircuit"
    SCHEDULE = "schedule"

    @staticmethod
    def is_known_event(event_name: str) -> bool:
        """Check if the event name is a known Socket.IO event."""
        return event_name in [event.value for event in SocketIOEventsInbound]
    

# class SocketIOEventsOutbound(Enum):
#     """Socket.IO outbound event names for nodejs-PoolController."""
#     CONFIG_LIGHTGROUP = "/config/lightGroup"
#     STATE_CIRCUIT_TOGGLESTATE = "/state/circuit/toggleState"
#     STATE_BODY_HEATMODE = "/state/body/heatMode"
#     STATE_BODY_SETPOINT = "/state/body/setPoint"
#     TEMPS = "/temps"
#     CHLORINATOR = "/chlorinator"
#     FILTER = "/filter"
#     CHEM_CONTROLLER = "/chemController"
#     CIRCUIT = "/circuit"
#     FEATURE = "/feature"
#     CIRCUITGROUP = "/circuitGroup"
#     LIGHTGROUP = "/lightGroup"
#     PANELMODE = "/panelMode"

#     @staticmethod
#     def is_known_event(event_name: str) -> bool:
#         """Check if the event name is a known Socket.IO event."""
#         return event_name in [event.value for event in SocketIOEventsOutbound]