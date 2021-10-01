import sys
from termcolor import colored

# Output Manager, manages output and dumps to files and stdout
class OutputManager(object):

    def __init__(self, colored=colored):
        self.out = ""
        self.colored = colored

    def add_general_info(self, infoname, infoval):
        self.out += "{:30s} {}\n".format(infoname, infoval)

    def add_cert_info(self, infoname, infoval):
        self.out += "  {:28s} {}\n".format(infoname, infoval)

    def add_general_info_ok(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "green"))

    def add_general_info_info(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "blue"))

    def add_general_info_warning(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "yellow"))

    def add_general_info_error(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "red"))

    def add_cert_info_ok(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "green"))

    def add_cert_info_info(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "blue"))

    def add_cert_info_warning(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "yellow"))

    def add_cert_info_error(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "red"))

    def add_remaining_time(self, certtype, certdate, level, remaining_days):
        if level == 0:
            color = "white"
        if level == 1:
            color = "green"
        if level == 2:
            color = "yellow"
        if level == 3:
            color = "red"

        self.out += "  {:28s} {} ({})\n".format(
            "{} Date".format(certtype),
            self.colored(certdate, color),
            self.colored(remaining_days, color)
        )

    def get_not_yet_valid(self, remaining_hours):
        return "Not yet valid, {:.0f} hours to validity, {} days".format(
                hours_to_valid, int(hours_to_valid / 24)
        )

    def get_expired(self, remaining_hours):
        return "Expired since {:.0f} hours, {} days".format(
                    -remaining_hours,
                    -int(remaining_hours / 24)
                )
    def get_hours_left(self, remaining_hours):
        return "{:.0f} hours left ({} days)".format(
                    remaining_hours,
                    int(remaining_hours / 24)
                )

    def get_months_left(self, remaining_hours):
        return "{:.0f} hours left, {} days, ~ {} months".format(
                remaining_hours,
                int(remaining_hours / 24),
                round(remaining_hours / 24 / 30)
        )

    def dump(self, file=sys.stdout):
        print(self.out, file=file)


    def dump_settings(self):
        sm = SettingsManager()

        print("Tests")
        for el in sm.test.items():
            print("  {} not before: {:4d} hours not after: {:4d} hours".format(
                self.colored("{:25s}".format(el[0]), "blue"),
                el[1]["start_hours"],
                el[1]["end_hours"])
            )

        print("\nCertifications")
        print("  {} not before: {:4d} days  not after: {:4d} days".format(
            self.colored("{:25s}".format("recovery"), "blue"),
            sm.recovery["start_day"],
            sm.recovery["end_day"])
        )

        print("\nVaccines")
        for vac in sm.vaccines.items():
            for el in vac[1].items():
                print("  {} {} not before: {:4d} days  not after: {:4d} days".format(
                    self.colored("{:12s}".format(el[0]), "blue"),
                    self.colored("{:12s}".format(Vaccine(vac[0]).get_pretty_name()), "yellow"),
                    el[1]["start_day"], el[1]["end_day"]
                ))
        print()

