from djitellopy import Tello
from Pose_Net import PoseNet
import cv2
import pygame
import numpy as np
import time
# Speed of the drone with maximum of 100
S = 10
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 120
model = PoseNet("posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite")

class Display(object):
    """ Tello display
        Press escape key to quit.
        The controls implemented:
            - T: Takeoff
            - L: Land
            - W, S, A, D: Forward, backward, left and right (x,y)
            - Arrow Keys: Up and down. (z)
            - Q and E: Counter clockwise and clockwise rotations (yaw)     
    """
    def __init__(self):
        # Init pygame
        pygame.init()

        # Create pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.y_velocity = 0
        self.x_velocity = 0
        self.z_velocity = 0
        self.yaw_velocity = 0
        self.speed = 50
        self.S = 10

        self.send_rc_control = False

        # Ticker implementation
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):
        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        stop = False
        while not stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame
            img_input = frame.copy()
            img_input = model.prepare_input(img_input)
            keypoints = model.predict_singlepose(img_input)
            
            BATTERY = "Battery: {}%; Speed: {}".format(self.tello.get_battery(),self.S)
            cv2.putText(frame, BATTERY, (5, 420 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            model.draw_pose(frame, keypoints)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()

    def keydown(self, key):
        """ Update values based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_a:       # set left velocity
            self.x_velocity = -self.S
        elif key == pygame.K_d:     # set right velocity
            self.x_velocity = self.S
        elif key == pygame.K_w:     # set forward velocity
            self.y_velocity = self.S
        elif key == pygame.K_s:     # set backward velocity
            self.y_velocity = -self.S
        elif key == pygame.K_UP:    # set up velocity
            self.z_velocity = self.S
        elif key == pygame.K_DOWN:  # set down velocity
            self.z_velocity = -self.S
        elif key == pygame.K_LEFT:     # set yaw counter clockwise velocity
            self.yaw_velocity = -self.S
        elif key == pygame.K_RIGHT:     # set yaw clockwise velocity
            self.yaw_velocity = self.S
        elif key == pygame.K_1:     # set  velocity
            self.S = 10
        elif key == pygame.K_2:     # set  velocity
            self.S = 20
        elif key == pygame.K_3:     # set  velocity
            self.S = 30
        elif key == pygame.K_4:     # set  velocity
            self.S = 40
        elif key == pygame.K_5:     # set  velocity
            self.S = 50
        elif key == pygame.K_6:     # set  velocity
            self.S = 60
        elif key == pygame.K_7:     # set  velocity
            self.S = 70
        elif key == pygame.K_8:     # set  velocity
            self.S = 80
        elif key == pygame.K_9:     # set  velocity
            self.S = 90
        elif key == pygame.K_0:     # set  velocity
            self.S = 100
        elif key == pygame.K_BACKSPACE:
            self.tello.emergency()
            
        

    def keyup(self, key):
        """ Update values for key release
        Arguments:
            key: pygame key
        """
        if key == pygame.K_a or key == pygame.K_d:          # set zero left/right velocity
            self.x_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:        # set zero forward/backward velocity
            self.y_velocity = 0
        elif key == pygame.K_UP or key == pygame.K_DOWN:    # set zero up/down velocity
            self.z_velocity = 0
        elif key == pygame.K_RIGHT or key == pygame.K_LEFT:        # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:         # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:         # land
            not self.tello.land()
            self.send_rc_control = False
        
        elif key == pygame.K_DELETE:
            self.tello.send_rc_control(0,0,0,100)
            time.sleep(0.5)
            self.tello.land()
        

    def update(self):
        """ Update and send all the events to the tello"""
        if self.send_rc_control:
            self.tello.send_rc_control(self.x_velocity, self.y_velocity,
                self.z_velocity, self.yaw_velocity)

def main():
    display = Display()
    display.run()

if __name__ == '__main__':
    main()