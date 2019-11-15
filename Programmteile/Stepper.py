
from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("a","nema")

motor.motor_run([19,21,26,13],0.001, 5000,0,0,"full",0)     #([pins], delay, steps, ccwise, verbose, "stepType", initDelay)