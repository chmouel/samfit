#!/usr/bin/env python
import subprocess

import tp

TP_USERNAME = 'chmouel'


class TRWorkoutID(object):
    def login(self, tp_username):
        password = subprocess.Popen(
            ["security", "find-generic-password", "-a",
             "chmouel", "-s", "trainingpeaks", "-w"],
            stdout=subprocess.PIPE
        ).communicate()[0].strip()
        self.tpsess = tp.TPconnect(tp_username, password)
        self.tpsess.init()


if __name__ == "__main__":
    d = TRWorkoutID()
    d.login(TP_USERNAME)
    
