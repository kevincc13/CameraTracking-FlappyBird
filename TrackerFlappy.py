import cv2 as cv
import sys
import numpy as np
import pygame
import random 
import threading
import time

sensitivity = int(2)

(major_ver, minor_ver, subminor_ver) = (cv.__version__).split('.')
def draw_floor():
    screen.blit(floor_surface,(floor_x_pos,900))
    screen.blit(floor_surface,(floor_x_pos + 576,900))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (700,random_pipe_pos - 300))
    return bottom_pipe,top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface,pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface,False,True)
            screen.blit(flip_pipe,pipe)

def check_collision(pipes):
    global can_score
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            can_score = True
            return False

    #if bird_rect.top <= -100 or bird_rect.bottom >= 900:
        #can_score = True
        #return False

    return True

def rotate_bird(bird):
    new_bird = bird
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100,bird_rect.centery))
    return new_bird,new_bird_rect

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)),True,(255,255,255))
        score_rect = score_surface.get_rect(center = (288,100))
        screen.blit(score_surface,score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render('Score: {}'.format(int(score)) , True, (255,255,255))
        score_rect = score_surface.get_rect(center = (288,100))
        screen.blit(score_surface,score_rect)

        high_score_surface = game_font.render('High score: {}'.format(int(high_score)),True,(255,255,255))
        high_score_rect = high_score_surface.get_rect(center = (288,850))
        screen.blit(high_score_surface,high_score_rect)

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score

def pipe_score_check():
    global score, can_score 
    
    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True

#pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 2, buffer = 1024)
pygame.init()
screen = pygame.display.set_mode((576,1024))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf',40)

# Game Variables
gravity = 1.25
bird_movement = 0
game_active = True
score = 0
high_score = 0
can_score = True
bg_surface = pygame.image.load('assets/background-day.png').convert()
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())
bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect()

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP,200)

# bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
# bird_surface = pygame.transform.scale2x(bird_surface)
# bird_rect = bird_surface.get_rect(center = (100,512))

pipe_surface = pygame.image.load('assets/pipe-green.png')
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE,1800)
pipe_height = [400,600,800]

game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (288,512))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
score_sound_countdown = 100
SCOREEVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SCOREEVENT,100)


if __name__ == '__main__' :

    # Set up tracker.
    # Instead of MIL, you can also use

    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    tracker_type = tracker_types[2]

    if int(minor_ver) < 3:
        tracker = cv.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv.TrackerCSRT_create()

    # Read video
    video = cv.VideoCapture(0)


    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()
    flipper = cv.flip(frame,1)
    
    # Define an initial bounding box
    bbox = (287, 23, 86, 320)

    # Uncomment the line below to select a different bounding box
    bbox = cv.selectROI(flipper, False)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(flipper, bbox)
      

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        flip = cv.flip(frame,1)
        combined_window = flip

        # Start timer
        timer = cv.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(combined_window)
      
        # Calculate Frames per second (FPS)
        fps = cv.getTickFrequency() / (cv.getTickCount() - timer);

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv.rectangle(combined_window, p1, p2, (255,0,0), 2, 1)
            x_m_point = float((int(bbox[0]) + int(bbox[0] + bbox[2]))/2)
            y_m_point = float((int(bbox[1]) + int(bbox[1] + bbox[3]))/2)
            cv.circle(combined_window, (int(x_m_point), int(y_m_point)), 5, (0,0,255), 5)
            x = x_m_point*sensitivity
            y = y_m_point*sensitivity
        else :
             #Tracking failure
            cv.putText(combined_window, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
        # Display tracker type on frame
        cv.putText(combined_window, tracker_type + " Tracker", (100,20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
        
        # Display FPS on frame
        cv.putText(combined_window, "FPS : " + str(int(fps)), (100,50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
        for event in pygame.event.get():
             if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active == False:
                    game_active = True
                    pipe_list.clear()
                    score = 0

             if event.type == SPAWNPIPE:
                  pipe_list.extend(create_pipe())

        screen.blit(bg_surface,(0,0))

        if game_active:
        # Bird
            screen.blit(bird_surface,(x,y))
            bird_rect = bird_surface.get_rect(center = ((x + 34),(y + 24)))
            print(bird_rect)
            game_active = check_collision(pipe_list)

        # Pipes
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
        
        # Score
            pipe_score_check()
            score_display('main_game')
        else:
            screen.blit(game_over_surface,game_over_rect)
            high_score = update_score(score,high_score)
            score_display('game_over')


    # Floor
        floor_x_pos -= 1
        draw_floor()
        if floor_x_pos <= -576:
             floor_x_pos = 0
    

        pygame.display.update()
        clock.tick(120)


        # Display result
        cv.imshow("Tracking", combined_window)

        # Exit if ESC pressed
        k = cv.waitKey(1) & 0xff
        if k == 27 : break


            
