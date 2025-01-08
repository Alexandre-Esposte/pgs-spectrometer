from motor.motor import Motor
from encoder.encoder import Encoder
from controller.controller import Controller
import time
import RPi.GPIO as gpio



controller = Controller()


init_angle = float(input('Informe o angulo inicial: '))
final_angle = float(input('Informe o angulo final: '))



controller.toAngle(init_angle, final_angle)


gpio.cleanup()