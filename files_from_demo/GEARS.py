import time
import math as m

import brickpi3
import grovepi as GP
from MPU9250 import MPU9250
import IR_Functions as IR


class GEARS:
    def __init__(self):
        """Initialize the GEARS class
        """
        # BrickPi3
        self.BP = brickpi3.BrickPi3()
        self.RMOTOR = self.BP.PORT_D
        self.LMOTOR = self.BP.PORT_A
        self.FMOTOR = self.BP.PORT_C

        # GrovePi
        self.FSENSOR = 4
        self.RSENSOR = 2
        self.IMU = MPU9250()
        IR.IR_setup(GP)

        time.sleep(.5)

        self.turn_time = 1.397
        self.out_array = []

        self.kP = 3
        self.kD = 2
        self.kI = 1.5
        self.iError = 0
        self.prevErr = 0

        time.sleep(.5)

    def traverse_maze(self):
        """Logic for traversing maze and creating distance direction array

        Returns:
            array: array of distance and direction and key values
        """
        max_right = 20
        max_front = 15
        speed = 180
        just_turned = False
        direction = 0
        distance = 0
        moves = [[7, 0], [0, 0]]

        try:
            while True:
                front_reading = GP.ultrasonicRead(self.FSENSOR)
                right_reading = GP.ultrasonicRead(self.RSENSOR)
                print(front_reading, right_reading)
                imu = self.IMU.readMagnet()
                mag_reading = m.sqrt(
                    imu['x'] ** 2 + imu['y'] ** 2 + imu['z'] ** 2)
                ir1, ir2 = IR.IR_Read(GP)
                ir_reading = (ir1 + ir2) / 2

                if mag_reading > 100 or ir_reading > 9:
                    self.turn_right()
                    self.iError, self.prevErr = 0, 0
                    moves[-1][1] = m.floor(distance)
                    direction += - 3 if direction == 3 else 1
                    distance = 0
                    if mag_reading > 100:
                        moves.append([5, mag_reading])
                    else:
                        moves.append([6, ir_reading])
                    moves.append([direction, 0])

                elif right_reading < max_right or just_turned:
                    if front_reading < max_front:
                        # Navigation
                        self.turn_left()
                        self.iError, self.prevErr = 0, 0

                        # Mapping
                        moves[-1][1] = m.floor(distance)
                        direction += 3 if direction == 0 else -1
                        moves.append([direction, 0])
                        distance = 0

                    else:
                        # Navigation
                        self.straight_control(speed, right_reading)

                        # Mapping
                        distance += .25641

                    just_turned = right_reading >= max_right
                    
                elif right_reading >= max_right:
                    # Navigation
                    if front_reading > max_front:
                        self.straight(speed)
                        time.sleep(1.4)
                        self.turn_right_PID(1.2)
                        just_turned = True
                    else:
                        self.turn_right()
                    self.iError, self.prevErr = 0, 0

                    # Mapping
                    distance += 4.10256
                    moves[-1][1] = m.floor(distance)
                    direction += - 3 if direction == 3 else 1
                    moves.append([direction, 0])
                    distance = 0
                    
                    # Straight for errors
                    self.straight(speed)
                    time.sleep(.5)
                    distance += 1.28205

                time.sleep(0.1)

        except KeyboardInterrupt:
            moves[-1][1] = m.floor(distance)
            moves.append([4, 0])
            self.out_array = moves
            self.stop()

        return self.out_array

    def straight(self, dps):
        """Set GEARS to go straight with wheels turning at desired dps

        Args:
            dps (float): Desired dps for wheels
        """
        self.BP.set_motor_dps(self.RMOTOR, dps)
        self.BP.set_motor_dps(self.LMOTOR, dps)

    def straight_control(self, dps, right_dist):
        """Set GEARS to go straight with control

        Args:
            right_dist (float): Distance from right wall
        """
        error = (6 - right_dist) if right_dist < 11 else -6
        # Positive error - deviating to the right
        # Negative error - deviating to the left
        pError = self.kP * error
        dError = self.kD * (error - self.prevErr) / 0.1
        self.iError += self.kI * (error - self.prevErr) * .5
        self.prevErr = error

        rChange = 1 + (pError + dError + self.iError) / 100
        lChange = 2 - rChange 

        self.BP.set_motor_dps(self.RMOTOR, dps * rChange)
        self.BP.set_motor_dps(self.LMOTOR, dps * lChange)

    def test_control(self):
        """Test the straigh_control() module
        """
        try:
            while True:
                right_reading = GP.ultrasonicRead(self.RSENSOR)
                self.straight_control(250, right_reading)

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def turn_clockwise(self, angle):
        """Make GEARS turn specific angle clockwise

        Args:
            angle (float): desired angle to turn clockwise by
        """
        time = angle * self.turn_time / 90

        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

        self.BP.set_motor_dps(self.RMOTOR, -180)
        self.BP.set_motor_dps(self.LMOTOR, 180)
        time.sleep(time)

        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

    def turn_right(self):
        """Make GEARS turn right
        """
        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

        self.BP.set_motor_dps(self.RMOTOR, -180)
        self.BP.set_motor_dps(self.LMOTOR, 180)
        time.sleep(self.turn_time)

        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

    def turn_right_PID(self, t):
        """Make GEARS turn right with offset from PID
        """
        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

        self.BP.set_motor_dps(self.RMOTOR, -180)
        self.BP.set_motor_dps(self.LMOTOR, 180)
        time.sleep(t)

        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

    def turn_left(self):
        """Make GEARS turn left
        """
        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

        self.BP.set_motor_dps(self.RMOTOR, 180)
        self.BP.set_motor_dps(self.LMOTOR, -180)
        time.sleep(self.turn_time)

        self.BP.set_motor_dps(self.RMOTOR, 0)
        self.BP.set_motor_dps(self.LMOTOR, 0)

    def show_label(self, index):
        """Turn front motor to show desired label

        Args:
            index (int): Label index
        """
        turn_speed = 54.125

        self.BP.set_motor_dps(self.FMOTOR, turn_speed)
        time.sleep(int(index))

        self.BP.set_motor_dps(self.FMOTOR, 0)

    def show_mag(self):
        """Display readings from IMU sensor 
        """
        average = 0
        for _ in range(20):
            imu = self.IMU.readMagnet()
            mag_reading = m.sqrt(
                imu['x'] ** 2 + imu['y'] ** 2 + imu['z'] ** 2)
            average += mag_reading
            time.sleep(.1)

        average /= 20
        print(average)

    def show_ir(self):
        """Display readings from IR sensor
        """
        average = 0
        for _ in range(20):
            ir1, ir2 = IR.IR_Read(GP)
            ir_reading = (ir1 + ir2) / 2
            average += ir_reading
            time.sleep(.1)
        average /= 20
        print(average)

    def stop(self):
        """Reset all BrickPi motors
        """
        self.BP.reset_all()
