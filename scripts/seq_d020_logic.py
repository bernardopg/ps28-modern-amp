#!/usr/bin/env python3
"""Zero-delay logic model of the CAPTURED seq-d020 netlist (not a hand-written FSM).

Behaviour per part comes from TI datasheets (TPS3808 SBVS050N p.7 td corners;
SN74LVC2G74 SCES203Q edge/clear; LVC gates). Analog levels, propagation delays,
power-up below VPOR, bounce and the TPA itself are NOT modelled: the testbench
supplies power-good, button and TPA FAULT/CLIP_OTW. Not hardware validation.
"""

from create_seq_d020 import parts

# TPS3808 SBVS050N p.7 sec.6.6: CT to VDD 180/300/420 ms, CT 180 nF 0.62/1.03/1.44 s.
TD_US = {"SEQ_CT1": (180_000, 420_000), "SEQ_CT2": (180_000, 420_000),
         "SEQ_CT3": (620_000, 1_440_000)}


class SeqLogic:
    def __init__(self, corner=0, inventory=None):
        self.parts = {p["ref"]: p for p in (inventory or parts())}
        self.corner = corner  # 0 = minimum td, 1 = maximum td
        self.ff = {r: False for r, p in self.parts.items() if p["value"] == "74LVC2G74"}
        self.clk = {r: False for r in self.ff}
        self.released_at = {r: None for r, p in self.parts.items() if p["value"] == "TPS3808G33"}
        self.pullups = {
            p["nets"]["2"] for p in self.parts.values()
            if p["lib_id"] == "Device:R" and p["nets"]["1"] == "SEQ_3V3"
        } | {"RAILS_OK"}  # R323 lives in power-d021

    def _eval(self, t, ext, nets):
        """One pass; returns new net dict. ext: externally driven nets (bool)."""
        od_low = {n: False for n in self.pullups}
        new = dict(ext)
        for ref, p in self.parts.items():
            n = p["nets"]
            if p["value"] == "TPS3808G33":
                mr = nets.get(n["3"], True)
                if not mr:
                    self.released_at[ref] = None
                elif self.released_at[ref] is None:
                    self.released_at[ref] = t
                td = TD_US[n["4"]][self.corner]
                if self.released_at[ref] is None or t - self.released_at[ref] < td:
                    od_low[n["1"]] = True
            elif p["value"] == "74LVC2G74":
                clk = nets.get(n["1"], False)
                if not nets.get(n["6"], False):
                    self.ff[ref] = False
                elif clk and not self.clk[ref]:
                    self.ff[ref] = nets.get(n["2"], False)
                self.clk[ref] = clk
                if n["5"]:
                    new[n["5"]] = self.ff[ref]
                if n["3"]:
                    new[n["3"]] = not self.ff[ref]
            elif p["value"] == "74LVC1G14":
                new[n["4"]] = not nets.get(n["2"], True)
            elif p["value"] == "74LVC1G32":
                new[n["4"]] = nets.get(n["1"], False) or nets.get(n["2"], False)
            elif p["value"] == "74LVC1G08":
                new[n["4"]] = nets.get(n["1"], False) and nets.get(n["2"], False)
            elif p["value"] == "74LVC1G07" and not nets.get(n["2"], True):
                od_low[n["4"]] = True
            elif p["value"] == "74LVC1G06" and nets.get(n["2"], False):
                od_low[n["4"]] = True
            elif p["ref"] == "R408":  # series resistor into TPA RESET (R9 pull-down)
                new["RESET"] = nets.get("RUN", False)
        for net, low in od_low.items():
            if net in ext and not ext[net]:
                low = True  # external open-drain (power-good) pulls low
            new[net] = not low
        return new

    def step(self, t, power_ok, button_pressed, fault, otw, nets=None):
        """power_ok: LM5164 PGOOD and TPS3700 window (open-drain into RAILS_OK).
        fault/otw: TPA open-drain outputs. Returns settled nets."""
        ext = {"RAILS_OK": power_ok, "START_DEB": not button_pressed,
               "FAULT": fault, "CLIP_OTW": otw}
        nets = dict(nets or {})
        nets.update({k: v for k, v in ext.items() if k != "RAILS_OK"})
        for _ in range(64):
            new = self._eval(t, ext, nets)
            if new == nets:
                return nets
            nets = new
        raise RuntimeError("Combinational loop did not settle")


def run(script, corner=0, dt=1_000, end=4_000_000):
    """script(t, nets) -> (power_ok, button, fault, otw). Returns [(t, nets)]."""
    model = SeqLogic(corner)
    nets, trace = {}, []
    for t in range(0, end + 1, dt):
        nets = model.step(t, *script(t, nets), nets)
        trace.append((t, nets))
    return trace
