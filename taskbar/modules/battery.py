import os

from gi.repository import GLib

class Battery:
    def __init__(self, label, BATTERY, AC):
        super().__init__()

        INTERVAL = 1

        self.label = label
        self.battery = BATTERY
        self.ac = AC

        self.curr_batt_perc = None
        self.orig_batt_value = None
        self.orig_acPower = None
        self.acPower = None

        self.powerSupply()

        GLib.timeout_add_seconds(INTERVAL, self.powerSupply)

    def powerSupply(self):
        try:
            if os.path.exists(self.battery):
                with open(self.battery, "r") as batt:
                    self.curr_batt_perc = int(batt.read().strip())
            else:
                print(f"{self.battery} not found.")
                return True

            if os.path.exists(self.ac):
                with open(self.ac, "r") as ac_power:
                    self.acPower = int(ac_power.read().strip())
            else:
                print(f"{self.ac} not found.")
                return True

            if self.curr_batt_perc != self.orig_batt_value or self.acPower != self.ac_power:
                self.orig_batt_value = self.curr_batt_perc
                self.ac_power = self.acPower

                self.powerSupply_Change()
            else:
                return True
        except OSError as e:
            print(f"There is an error {e}")
        
        return True

    def powerSupply_Change(self):
        try:
            if self.acPower == 1:
                    self.label.set_label(f" {self.curr_batt_perc}%")
            elif self.curr_batt_perc is not None:
                if self.curr_batt_perc <= 15:
                    self.label.set_label(f"   {self.curr_batt_perc}%")
                elif self.curr_batt_perc <= 25:
                    self.label.set_label(f"   {self.curr_batt_perc}%")
                elif self.curr_batt_perc <= 50:
                    self.label.set_label(f"   {self.curr_batt_perc}%")
                elif self.curr_batt_perc <= 75:
                    self.label.set_label(f"   {self.curr_batt_perc}%")
                else:
                    self.label.set_label(f"   {self.curr_batt_perc}%")                
            else:
                print(f"Battery status is None")
        except OSError as e:
            print(f"There is an issue with your battery settings: {e}")