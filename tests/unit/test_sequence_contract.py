import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from sequence_contract import (
    Observations,
    Sequencer,
    State,
    latency_qualified,
    reset_pull_down_bound,
)

GOOD = Observations(
    rails_valid=True,
    control_valid=True,
    reference_valid=True,
    vmid_valid=True,
    drivers_quiet=True,
    preclose_match=True,
    dc_a_valid=True,
    dc_b_valid=True,
    fault_high=True,
    otw_high=True,
    open_confirmed=False,
    discharge_off_confirmed=True,
    close_confirmed=True,
)


OPEN = replace(GOOD, open_confirmed=True, close_confirmed=False)


def boot(s, finish=True):
    s.step(0, OPEN)
    s.step(360_000, OPEN)
    s.step(360_001, replace(OPEN, button=True))
    s.step(360_002, OPEN)  # discharge off confirmed before connection command
    s.step(360_003, GOOD)  # physical close confirmed before RESET
    s.step(360_004, replace(GOOD, fault_high=False))
    s.step(360_005, GOOD)
    s.step(360_006, GOOD)
    return s.step(372_006, GOOD) if finish else None


class SequencingTests(unittest.TestCase):
    def test_observed_precharge_before_audio_and_fault_mask_no_retry(self):
        s = Sequencer()
        self.assertTrue(boot(s).audio_enable)
        c = s.step(372_007, replace(GOOD, fault_high=False, open_confirmed=False))
        self.assertFalse(c.reset_release)
        self.assertFalse(c.input_connect)
        self.assertFalse(c.audio_enable)
        self.assertFalse(c.discharge)
        self.assertEqual(s.state, State.FAULT_LATCHED)
        # RESET-induced FAULT high is NOT a new manual request.
        for t in [372_008, 400_000, 800_000]:
            c = s.step(t, GOOD)
            self.assertFalse(c.reset_release)
            self.assertFalse(c.audio_enable)

    def test_button_held_across_brownout_does_not_queue_restart(self):
        s = Sequencer()
        s.step(0, replace(OPEN, rails_valid=False, button=True))
        s.step(1, replace(OPEN, button=True))
        s.step(400_000, replace(OPEN, button=True))
        self.assertEqual(s.state, State.QUALIFY)
        s.step(400_001, OPEN)
        self.assertEqual(s.state, State.WAIT_REQUEST)
        s.step(400_002, replace(OPEN, button=True))
        self.assertEqual(s.state, State.WAIT_DRIVERS)

    def test_300ms_typical_single_stage_not_minimum250ms(self):
        self.assertLess(180_000, 250_000)
        self.assertGreaterEqual(Sequencer.BOOT_HOLD_US, 250_000)
        s = Sequencer()
        s.step(0, GOOD)
        c = s.step(250_000, replace(GOOD, button=True))
        self.assertFalse(c.reset_release)
        self.assertFalse(c.input_connect)

    def test_both_inputs_required_and_initial_fault_signature_observed(self):
        for field in ["dc_a_valid", "dc_b_valid"]:
            s = Sequencer()
            boot(s)
            c = s.step(400_000, replace(GOOD, **{field: False}))
            self.assertFalse(c.audio_enable)
        s = Sequencer()
        for t, o in [
            (0, OPEN),
            (360_000, OPEN),
            (360_001, replace(OPEN, button=True)),
            (360_002, OPEN),
            (360_003, GOOD),
            (400_000, GOOD),
        ]:
            c = s.step(t, o)
        self.assertFalse(c.audio_enable)  # initial FAULT high can be RESET masking
        self.assertFalse(s.fault_armed)
        c = s.step(1_900_000, GOOD)
        self.assertFalse(c.reset_release)
        self.assertEqual(s.state, State.FAULT_LATCHED)

    def test_unconfirmed_isolation_cannot_discharge_receiver(self):
        s = Sequencer()
        self.assertFalse(s.step(0, Observations()).discharge)
        self.assertTrue(s.step(1, Observations(open_confirmed=True)).discharge)
        s = Sequencer()
        s.step(0, OPEN)
        s.step(360_000, OPEN)
        s.step(360_001, replace(OPEN, button=True))
        c = s.step(360_002, replace(OPEN, discharge_off_confirmed=False))
        self.assertFalse(c.input_connect)
        c = s.step(360_003, OPEN)
        self.assertTrue(c.input_connect)
        self.assertFalse(c.reset_release)

    def test_all_domains_and_phase_actions_trip_without_automatic_retry(self):
        for field in ["rails_valid", "control_valid", "reference_valid", "vmid_valid"]:
            s = Sequencer()
            boot(s)
            c = s.step(400_000, replace(GOOD, **{field: False}))
            self.assertFalse(c.input_connect)
            self.assertFalse(c.audio_enable)
        s = Sequencer()
        boot(s)
        self.assertFalse(
            s.step(400_000, replace(GOOD, phase_or_volume_event=True)).audio_enable
        )

    def test_unknown_or_typical_delay_cannot_prove100us(self):
        self.assertFalse(latency_qualified([None, 0.0079, None]))
        self.assertFalse(latency_qualified([60, 50]))
        self.assertTrue(latency_qualified([20, 20, 20]))  # arithmetic only
        with self.assertRaises(ValueError):
            latency_qualified([-1])

    def test_reset_pull_down_required_worst_case_not_10k_safe_claim(self):
        self.assertGreater(reset_pull_down_bound(10_000, 0.01, driver_ioff_a=0), 0.8)
        self.assertAlmostEqual(reset_pull_down_bound(4700, 0.01), 0.52217)
        self.assertLess(reset_pull_down_bound(4700, 0.01), 0.8)
        with self.assertRaises(ValueError):
            reset_pull_down_bound(-1, 0.01)

    def test_rearm_requires_fresh_dc_dwell_without_power_loss(self):
        s = Sequencer()
        boot(s)
        s.step(400_000, replace(GOOD, fault_high=False))
        for t, o in [
            (412_000, OPEN),
            (412_001, replace(OPEN, button=True)),
            (412_002, OPEN),
            (412_003, GOOD),
            (412_004, replace(GOOD, fault_high=False)),
            (412_005, GOOD),
        ]:
            s.step(t, o)
        self.assertFalse(s.step(412_006, GOOD).audio_enable)
        self.assertTrue(s.step(424_006, GOOD).audio_enable)

    def test_close_loss_match_loss_and_contradictory_feedback_fail_closed(self):
        s = Sequencer()
        boot(s, finish=False)
        self.assertFalse(
            s.step(372_006, replace(GOOD, close_confirmed=False)).audio_enable
        )
        self.assertEqual(s.state, State.FAULT_LATCHED)
        s = Sequencer()
        for t, o in [
            (0, OPEN),
            (360_000, OPEN),
            (360_001, replace(OPEN, button=True)),
            (360_002, OPEN),
        ]:
            s.step(t, o)
        self.assertFalse(
            s.step(360_003, replace(OPEN, preclose_match=False)).input_connect
        )
        self.assertEqual(s.state, State.FAULT_LATCHED)
        s = Sequencer()
        boot(s)
        c = s.step(400_000, replace(GOOD, open_confirmed=True))
        self.assertFalse(c.audio_enable)
        self.assertFalse(c.input_connect)
        self.assertFalse(c.discharge)

    def test_open_ack_required_until_first_connection_command(self):
        for lost in (GOOD, replace(OPEN, open_confirmed=False)):
            with self.subTest(lost=lost):
                s = Sequencer()
                for t, o in [
                    (0, OPEN),
                    (360_000, OPEN),
                    (360_001, replace(OPEN, button=True)),
                ]:
                    s.step(t, o)
                c = s.step(360_002, lost)
                self.assertEqual(s.state, State.FAULT_LATCHED)
                self.assertFalse(c.input_connect)
                self.assertFalse(c.reset_release)
                self.assertFalse(c.audio_enable)
                self.assertFalse(c.discharge)

    def test_timestamp_reversal_rejected(self):
        s = Sequencer()
        s.step(10, GOOD)
        with self.assertRaises(ValueError):
            s.step(9, GOOD)


if __name__ == "__main__":
    unittest.main()
