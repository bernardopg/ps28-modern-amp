import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from create_seq_d020 import generate, parts, window_thresholds
from seq_d020_logic import run
from sequence_contract import Sequencer


def tpa(fault_script=lambda t: True):
    """TPA stand-in: RESET low forces FAULT high (SLASEA8A sec.9.4.x)."""
    def fault(t, nets):
        return True if not nets.get("RESET", False) else fault_script(t)
    return fault


def script(press=(), power=lambda t: True, fault=tpa(), otw=lambda t: True):
    def s(t, nets):
        pressed = any(a <= t < b for a, b in press)
        return power(t), pressed, fault(t, nets), otw(t)
    return s


def first(trace, net, value=True, after=0):
    return next((t for t, n in trace if t >= after and n.get(net) == value), None)


def precharge_dc(delay_us=150_000, state=None):
    """Pin windows valid delay_us after RESET release (TPA Fig.32 stand-in), else invalid."""
    state = {} if state is None else state

    def dc(t, nets):
        if not nets.get("RESET", False):
            state.pop("rel", None)
            return False
        return t - state.setdefault("rel", t) >= delay_us
    return dc


def d019_script(press, fault, dc, power=lambda t: True):
    def s(t, nets):
        return (power(t), any(a <= t < b for a, b in press), fault(t, nets), True, dc(t, nets))
    return s


def started_tpa(start_us):
    """FAULT low during start, high 200 ms later (contract START_AVDD), stays high."""
    state = {}

    def fault(t, nets):
        if not nets.get("RESET", False):
            state.pop("rel", None)
            return True
        rel = state.setdefault("rel", t)
        return t - rel >= 200_000
    return fault


class SeqD020Tests(unittest.TestCase):
    def test_hold_is_at_least_contract_minimum_and_press_before_is_ignored(self):
        for corner in (0, 1):
            tr = run(script(press=[(300_000, 350_000)]), corner, end=2_000_000)
            self.assertIsNone(first(tr, "RUN"))
            qual = first(tr, "RAILS_QUAL")
            self.assertGreaterEqual(qual, Sequencer.BOOT_HOLD_US)

    def test_held_button_cannot_queue_start(self):
        tr = run(script(press=[(0, 2_000_000)]), 1, end=2_000_000)
        self.assertIsNone(first(tr, "RUN"))
        tr = run(script(press=[(0, 1_000_000), (1_200_000, 1_300_000)]), 1, end=2_000_000)
        self.assertEqual(first(tr, "RUN"), 1_200_000)

    def test_start_requires_otw_high(self):
        tr = run(script(press=[(900_000, 950_000)], otw=lambda t: False), 1, end=1_500_000)
        self.assertIsNone(first(tr, "RUN"))

    def test_fault_after_arming_latches_until_new_hold_and_new_press(self):
        state = {}
        base = started_tpa(900_000)

        def fault(t, nets):
            ok = base(t, nets)
            if t >= 1_500_000 and nets.get("RESET", False) and not state.get("tripped"):
                state["tripped"] = t
                return False
            return ok
        press = [(900_000, 950_000), (1_600_000, 1_650_000), (2_400_000, 2_450_000)]
        for corner in (0, 1):
            state.clear()
            tr = run(script(press=press, fault=fault), corner, end=3_000_000)
            nets = dict(tr)
            self.assertTrue(nets[1_400_000]["RUN"] and not nets[1_400_000]["NOT_ARMED"])
            self.assertFalse(nets[1_500_000]["RUN"])
            self.assertFalse(nets[1_500_000]["RESET"])
            self.assertFalse(nets[2_300_000]["RUN"])  # press inside new hold ignored
            self.assertTrue(nets[2_450_000]["RUN"])

    def test_start_timeout_trips_when_fault_never_toggles(self):
        for corner in (0, 1):
            tr = run(script(press=[(900_000, 950_000)]), corner, end=4_000_000)
            on = first(tr, "RUN")
            off = first(tr, "RUN", False, after=on)
            self.assertGreaterEqual(off - on, 620_000)
            self.assertLessEqual(off - on, Sequencer.START_TIMEOUT_US + 1_000)

    def test_power_loss_drops_reset_immediately(self):
        tr = run(script(press=[(900_000, 950_000)], fault=started_tpa(900_000),
                        power=lambda t: t < 1_500_000), 1, end=2_000_000)
        nets = dict(tr)
        self.assertTrue(nets[1_499_000]["RESET"])
        self.assertFalse(nets[1_500_000]["RESET"])

    def test_capture_wiring_and_scope(self):
        nets = {p["ref"]: p["nets"] for p in parts()}
        self.assertEqual(nets["U406"]["6"], "RAILS_QUAL")
        self.assertEqual(nets["U406"]["2"], "CLIP_OTW")
        self.assertEqual((nets["U407"]["1"], nets["U407"]["6"]), ("FAULT", "RUN"))
        self.assertEqual(nets["R408"], {"1": "RESET_GO", "2": "RESET"})
        self.assertEqual((nets["U414"]["3"], nets["U414"]["4"]), ("RUN", None))  # CT open
        rails = {n for p in parts() for n in p["nets"].values()}
        self.assertFalse({"INPUT_A", "INPUT_B", "DIFF_P", "SPK_P"} & rails)
        self.assertNotIn("PVDD", rails)  # logic never touches PVDD directly

    def test_analog_windows_bracket_d018_rails(self):
        w = window_thresholds()
        # ANALOG_12V = AUX_RAW (11.69-12.50 V) minus D201/R201 drop; D-018 floor 8 V.
        self.assertGreater(w["ANALOG_UV"][0], 8.0)
        self.assertLess(w["ANALOG_UV"][2], 10.5)
        self.assertGreater(w["ANALOG_OV"][0], 12.5)
        self.assertLess(w["ANALOG_OV"][2], 14.0)
        # VMID = ANALOG_12V / 2 (75/75 divider): ~4.4-6.25 V over the ANALOG window.
        self.assertLess(w["VMID_UV"][2], 8.711 / 2)
        self.assertGreater(w["VMID_OV"][0], 12.5 / 2)
        nets = {p["ref"]: p["nets"] for p in parts()}
        for ref in ("U412", "U413"):
            self.assertEqual((nets[ref]["1"], nets[ref]["6"]), ("RAILS_OK", "RAILS_OK"))

    def test_d019_order_relay_then_reset_then_dc_dwell_then_audio(self):
        for corner in (0, 1):
            tr = run(d019_script([(900_000, 950_000)], started_tpa(0), precharge_dc()), corner,
                     end=2_500_000)
            run_on = first(tr, "RUN")
            reset_on = first(tr, "RESET")
            audio_on = first(tr, "AUDIO_EN")
            # RESET 12-28 ms after the relay command (relay operate 3 ms max, Omron K106).
            self.assertGreaterEqual(reset_on - run_on, 12_000)
            self.assertLessEqual(reset_on - run_on, 28_000 + 1_000)
            # Audio only after arming (FAULT rise 200 ms after RESET) and DC dwell >= 12 ms.
            dc_valid = reset_on + 150_000
            armed = first(tr, "NOT_ARMED", False, after=run_on)
            self.assertGreaterEqual(audio_on - max(dc_valid, armed), 12_000)
            for t, n in tr:
                if n.get("AUDIO_EN"):
                    self.assertTrue(n["RUN"] and n["RESET"] and not n["NOT_ARMED"], t)

    def test_dc_loss_after_unmute_latches_off_and_mutes(self):
        state = {}
        base = precharge_dc(state=state)

        def dc(t, nets):
            return base(t, nets) and not (1_600_000 <= t < 1_700_000)
        tr = run(d019_script([(900_000, 950_000)], started_tpa(0), dc), 1, end=2_200_000)
        nets = dict(tr)
        self.assertTrue(nets[1_599_000]["AUDIO_EN"])
        self.assertFalse(nets[1_600_000]["AUDIO_EN"] or nets[1_600_000]["RUN"] or nets[1_600_000]["RESET"])
        self.assertFalse(nets[2_200_000]["RUN"])  # no auto-restart when DC returns

    def test_precharge_never_valid_times_out(self):
        for corner in (0, 1):
            tr = run(d019_script([(900_000, 950_000)], started_tpa(0), lambda t, n: False), corner,
                     end=3_500_000)
            on = first(tr, "RUN")
            off = first(tr, "RUN", False, after=on)
            self.assertIsNone(first(tr, "AUDIO_EN"))
            self.assertLessEqual(off - on, Sequencer.START_TIMEOUT_US + 1_000)

    @unittest.skipUnless(Path("/usr/share/kicad/symbols").is_dir(), "needs KiCad stock symbol libraries")
    def test_generator_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s"
            generate(out)
            self.assertTrue((out / "libraries/PS28_SEQ.kicad_sym").exists())
            with self.assertRaises(FileExistsError):
                generate(out)


if __name__ == "__main__":
    unittest.main()
