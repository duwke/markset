from pymavlink import mavutil
from datetime import datetime
import time
import logging


class BoatControl:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.

    def __init__(self):
        self.master_ = mavutil.mavlink_connection('udpout:10.0.0.2:14550', 57600, 253)
        self.wait_conn()
        logging.warning("mavproxy connection " + str(self.master_))

    def wait_conn(self):
        """
        Sends a ping to stabilish the UDP communication and awaits for a response
        """
        msg = None
        while not msg:
            self.master_.mav.ping_send(
                int(time.time() * 1e6), # Unix time in microseconds
                0, # Ping number
                0, # Request ping of all systems
                0 # Request ping of all components
            )
            msg = self.master_.recv_match()
            time.sleep(0.5)
    def send_cmd(self, command, p1, p2, p3, p4, p5, p6, p7, target_sysid=None, target_compid=None):
        """Send a MAVLink command long."""
        self.master_.mav.command_long_send(target_sysid, target_compid, command, 1,  # confirmation
                                   p1, p2, p3, p4, p5, p6, p7)


    def run_cmd(self, command, p1, p2, p3, p4, p5, p6, p7, want_result=mavutil.mavlink.MAV_RESULT_ACCEPTED,
                 timeout=10, quiet=False):
        print('running cmd')
        target_sysid=self.master_.target_system
        target_compid=self.master_.target_component
        self.send_cmd(command, p1, p2, p3, p4, p5, p6, p7, target_sysid, target_compid)
        #self.run_cmd_get_ack(command, want_result, timeout, quiet=quiet)


    def run_cmd_get_ack(self, command, want_result, timeout, quiet=False):
        tstart = datetime.now()
        while True:
            delta_time = datetime.now() - tstart
            if delta_time.total_seconds() > timeout:
               print('ERROR', "Did not get good COMMAND_ACK within %fs" % timeout)
               raise Exception("Did not get good COMMAND_ACK within %fs" % timeout)
            m = self.master_.recv_match(type='COMMAND_ACK',
                                    blocking=True,
                                    timeout=0.1)
            if m is None:
                continue
            if not quiet:
                print("ACK received: %s" % (str(m)))
            if m.command == command:
                if m.result != want_result:
                    raise ValueError("Expected %s got %s" % (want_result,
                                                            m.result))
                break


    def arm(self):
        print('motors armed?', self.master_.motors_armed())

        time.sleep(1)

        print('arming throttle...')

        p2 = 0


        self.run_cmd(
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            1,  # param1 (1 to indicate arm)
            p2,  # param2  (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            0
        )

        self.master_.motors_armed_wait()

        print('motors armed:', self.master_.motors_armed())

    def disarm(self):
        p2 = 0

        print('attempt to disarm rover')

        self.run_cmd(
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            0,  # param1 (1 to indicate arm)
            p2,  # param2  (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6:q
            0
        )


        self.master_.motors_disarmed_wait()

        print('motors armed:', self.master_.motors_armed())
