#!/usr/bin/env python3
"""Executable hardware-sequencing specification, NOT firmware or physical protection.

Inputs are observations/commands requiring real circuits. Unknown propagation bounds
remain unknown: this model cannot prove D-019 latency or terminal voltages.
"""

from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    SAFE = "SAFE"
    QUALIFY = "QUALIFY"
    WAIT_REQUEST = "WAIT_REQUEST"
    WAIT_DRIVERS = "WAIT_DRIVERS"
    CONNECT_QUIET = "CONNECT_QUIET"
    START_AVDD = "START_AVDD"
    PRECHARGE = "PRECHARGE"
    RUN = "RUN"
    FAULT_LATCHED = "FAULT_LATCHED"


@dataclass(frozen=True)
class Observations:
    rails_valid: bool = False  # includes RAW, actual TPA supplies, protected, PVDD
    control_valid: bool = False
    reference_valid: bool = False
    vmid_valid: bool = False
    drivers_quiet: bool = False
    preclose_match: bool = False  # BOTH isolated plates versus receivers, <=10mV
    dc_a_valid: bool = False
    dc_b_valid: bool = False
    fault_high: bool = False
    otw_high: bool = False
    button: bool = False
    open_confirmed: bool = False  # physical isolation, not merely GPIO command
    discharge_off_confirmed: bool = False
    close_confirmed: bool = False
    phase_or_volume_event: bool = False

    @property
    def valid(self):
        return (
            self.rails_valid
            and self.control_valid
            and self.reference_valid
            and self.vmid_valid
            and not (self.open_confirmed and self.close_confirmed)
        )


@dataclass(frozen=True)
class Commands:
    reset_release: bool = False
    input_connect: bool = False
    audio_enable: bool = False
    discharge: bool = False


class Sequencer:
    # TPS3808 two fixed stages: each 180/300/420ms => minimum360ms,
    # NOT a single "300ms" timer (minimum180ms < TI recommendation250ms).
    BOOT_HOLD_US = 360_000
    REARM_US = 12_000  # CT-open stage guaranteed minimum; event capture still TBD
    DC_DWELL_US = 12_000
    START_TIMEOUT_US = 1_440_000  # proposed timeout, NOT guaranteed TPA startup

    def __init__(self):
        self.state = State.SAFE
        self.valid_since = None
        self.last_fault_fall = None
        self.start_since = None
        self.dc_since = None
        self.previous_button = False
        self.previous_fault = False
        self.last_time = -1
        self.fault_armed = False
        self.start_fault_low_seen = False
        self.latched_since = None

    def step(self, time_us, obs):
        if not isinstance(time_us, int) or time_us < 0 or time_us < self.last_time:
            raise ValueError("Time must be monotonic nonnegative integer microseconds")
        self.last_time = time_us
        previous_state = self.state
        rising_request = obs.button and not self.previous_button
        falling_fault = self.previous_fault and not obs.fault_high
        self.previous_button = obs.button  # held request cannot queue across PG loss
        self.previous_fault = obs.fault_high
        if falling_fault:
            self.last_fault_fall = time_us
        if not obs.valid:
            self.valid_since = None
            self.dc_since = None
            self.state = (
                State.FAULT_LATCHED
                if self.state not in (State.SAFE, State.QUALIFY)
                else State.SAFE
            )
        elif self.valid_since is None:
            self.valid_since = time_us
        active = (
            State.WAIT_DRIVERS,
            State.CONNECT_QUIET,
            State.START_AVDD,
            State.PRECHARGE,
            State.RUN,
        )
        if self.state in active and self.fault_armed and not obs.fault_high:
            self.state = State.FAULT_LATCHED
        if self.state in active and obs.phase_or_volume_event:
            self.state = State.FAULT_LATCHED  # no hot switching/retry silently
        if self.state == State.WAIT_DRIVERS and not obs.open_confirmed:
            self.state = State.FAULT_LATCHED
        connected_states = (
            State.CONNECT_QUIET,
            State.START_AVDD,
            State.PRECHARGE,
            State.RUN,
        )
        if (
            self.state == State.CONNECT_QUIET
            and not obs.close_confirmed
            and not obs.preclose_match
        ):
            self.state = State.FAULT_LATCHED
        if (
            self.state in (State.START_AVDD, State.PRECHARGE, State.RUN)
            and not obs.close_confirmed
        ):
            self.state = State.FAULT_LATCHED
        if self.state in connected_states and not obs.discharge_off_confirmed:
            self.state = State.FAULT_LATCHED
        if (
            self.state in (State.CONNECT_QUIET, State.START_AVDD, State.PRECHARGE)
            and not obs.drivers_quiet
        ):
            self.state = State.FAULT_LATCHED
        if self.state == State.RUN and not (
            obs.dc_a_valid and obs.dc_b_valid and obs.close_confirmed
        ):
            self.state = State.FAULT_LATCHED
        if (
            self.state in (State.START_AVDD, State.PRECHARGE)
            and time_us - self.start_since >= self.START_TIMEOUT_US
        ):
            self.state = State.FAULT_LATCHED
        new_trip = (
            self.state == State.FAULT_LATCHED and previous_state != State.FAULT_LATCHED
        )
        if new_trip:
            self.latched_since = time_us
            self.dc_since = None
        hold_ready = (
            self.valid_since is not None
            and time_us - self.valid_since >= self.BOOT_HOLD_US
        )
        rearm_ready = (
            self.last_fault_fall is None
            or time_us - self.last_fault_fall >= self.REARM_US
        )
        if self.state == State.SAFE and obs.valid:
            self.state = State.QUALIFY
        elif (
            self.state in (State.QUALIFY, State.FAULT_LATCHED)
            and not new_trip
            and (
                self.latched_since is None
                or time_us - self.latched_since >= self.REARM_US
            )
            and hold_ready
            and rearm_ready
            and not obs.button
        ):
            self.state = State.WAIT_REQUEST
        elif (
            self.state == State.WAIT_REQUEST
            and rising_request
            and hold_ready
            and rearm_ready
            and obs.otw_high
            and obs.open_confirmed
            and not obs.close_confirmed
        ):
            self.state = State.WAIT_DRIVERS
            self.fault_armed = False
            self.start_fault_low_seen = False
            self.dc_since = None
        elif (
            self.state == State.WAIT_DRIVERS
            and obs.drivers_quiet
            and obs.preclose_match
            and obs.discharge_off_confirmed
        ):
            self.state = State.CONNECT_QUIET
        elif (
            self.state == State.CONNECT_QUIET
            and obs.drivers_quiet
            and obs.close_confirmed
        ):
            self.state = State.START_AVDD
            self.start_since = time_us
        elif self.state == State.START_AVDD:
            if not obs.fault_high:
                self.start_fault_low_seen = True
            elif self.start_fault_low_seen:
                self.fault_armed = True
                self.dc_since = None
                self.state = State.PRECHARGE
        elif self.state == State.PRECHARGE:
            if (
                obs.drivers_quiet
                and obs.dc_a_valid
                and obs.dc_b_valid
                and obs.fault_high
            ):
                if self.dc_since is None:
                    self.dc_since = time_us
                elif time_us - self.dc_since >= self.DC_DWELL_US:
                    self.state = State.RUN
            else:
                self.dc_since = None
        commands = Commands(
            reset_release=self.state in (State.START_AVDD, State.PRECHARGE, State.RUN),
            input_connect=self.state
            in (State.CONNECT_QUIET, State.START_AVDD, State.PRECHARGE, State.RUN),
            audio_enable=self.state == State.RUN,
            discharge=self.state
            in (State.SAFE, State.QUALIFY, State.WAIT_REQUEST, State.FAULT_LATCHED)
            and obs.open_confirmed
            and not obs.close_confirmed,
        )
        self.assert_invariants(obs, commands)
        return commands

    def assert_invariants(self, obs, commands):
        if commands.audio_enable and not (
            obs.valid
            and commands.input_connect
            and commands.reset_release
            and obs.close_confirmed
            and obs.discharge_off_confirmed
            and obs.dc_a_valid
            and obs.dc_b_valid
            and self.fault_armed
            and obs.fault_high
        ):
            raise AssertionError("Audio before qualification/FAULT arming")
        if commands.discharge and (commands.input_connect or not obs.open_confirmed):
            raise AssertionError("Discharge without confirmed physical isolation")
        if commands.input_connect and not obs.valid:
            raise AssertionError("Connection without valid domains")


def reset_pull_down_bound(
    resistance_ohm, tolerance, tpa_leakage_a=100e-6, driver_ioff_a=10e-6
):
    if (
        resistance_ohm <= 0
        or not 0 <= tolerance < 1
        or min(tpa_leakage_a, driver_ioff_a) < 0
    ):
        raise ValueError("Invalid resistor/leakage envelope")
    return resistance_ohm * (1 + tolerance) * (tpa_leakage_a + driver_ioff_a)


def latency_qualified(delay_maxima_us, budget_us=100):
    """Typical/nominal delays MUST be represented as None, never as maxima."""
    if not delay_maxima_us or any(v is None for v in delay_maxima_us):
        return False
    if budget_us <= 0 or any(v < 0 for v in delay_maxima_us):
        raise ValueError("Invalid delay envelope")
    return sum(delay_maxima_us) <= budget_us
