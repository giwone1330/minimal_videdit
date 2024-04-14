# -*- coding:utf-8 -*-
import cv2
import pygame
import os
import math
import subprocess

# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)



def main():
    pygame.init()
    basedir = os.path.dirname(os.path.abspath(__file__))
    videosdir = os.path.join(basedir, 'videos')
    os.makedirs(videosdir, exist_ok=True)

    for i, file in enumerate(os.listdir(videosdir)):
        print("[{}] {}".format(i, file))
        if i == len(os.listdir(videosdir))-1:
            vidname = os.listdir(videosdir)[int(input("choose video No. : "))]
    videodir = os.path.join('videos', vidname)
    outputdir = os.path.join('videos', vidname.split('.')[0])
    name, _ = os.path.splitext(os.path.basename(vidname))

    # # making images labes temp folder for selected video
    # outputsdir = os.path.join(basedir, 'output')
    # os.makedirs(outputsdir, exist_ok=True)


    # Load video
    cap = cv2.VideoCapture(videodir)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    framems = int(1000/fps)
    targetms = framems
    totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cap.get(cv2.CAP_PROP_FOURCC)

    searchspeed = 1
    lstep = 1
    rstep = 1

    target_frame = 0

    x1, y1, x2, y2 = width//2-5, height//2-5, width//2+5, height//2+5

    # print(fps, width, height, fourcc)
    # print(cap.get(cv2.CAP_PROP_POS_FRAMES))

    # usemouse = True
    # usekey = False
    success, frame = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("bbox")
    clock = pygame.time.Clock()
    color = (255, 255, 255)
    idx = 7
    mask = False # initial state
    crop = False # initial state
    pressed = False
    lclk = 0
    rclk = 0
    lcnt = 0
    rcnt = 0
    lms = 4
    rms = 4
    loopms = 0
    pause = True
    pause_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)  # get current frame
    target_frame = pause_frame

    run = True
    while run:
        pygame.time.delay(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        tick = clock.tick()
        lclk += tick
        rclk += tick

        keys = pygame.key.get_pressed()

        # left,top
        if lclk >= lms:
            lcnt += math.log(1 + lclk-lms)
            lstep = 1
            if lcnt >= lms:
                lstep = 1 + int(lcnt//lms)
                lcnt = lcnt % lms
            lclk = 0
            if keys[pygame.K_w]:
                if lstep < y1:
                    y1 -= lstep
            if keys[pygame.K_s]:
                if lstep + y1 < y2:
                    y1 += lstep
            if keys[pygame.K_a]:
                if lstep < x1:
                    x1 -= lstep
            if keys[pygame.K_d]:
                if lstep + x1 < x2:
                    x1 += lstep

        # bottom right
        if rclk >= rms:
            rcnt += math.log(1 + rclk-rms)
            rstep = 1
            if rcnt >= rms:
                rstep = 1 + int(rcnt//rms)
                rcnt = rcnt % rms
            rclk = 0
            if keys[pygame.K_UP]:
                if rstep + y1 < y2:
                    y2 -= rstep
            if keys[pygame.K_DOWN]:
                if rstep + y2 < height-1:
                    y2 += rstep
            if keys[pygame.K_LEFT]:
                if rstep + x1 < x2:
                    x2 -= rstep
            if keys[pygame.K_RIGHT]:
                if rstep + x2 < width-1:
                    x2 += rstep

        # key input for pause
        if keys[pygame.K_p]:
            pause = True
            pause_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) - \
                1  # get current frame
            target_frame = pause_frame
        # key input for video start
        if keys[pygame.K_o]:
            pause = False
            loopms = 0
            targetms = framems
            searchspeed = 1
        # in pause state should go back and fourth,
        # when restart, run from the current showing frame
        if keys[pygame.K_i] and searchspeed < 30:
            searchspeed += 1
        if keys[pygame.K_k] and searchspeed > 1:
            searchspeed -= 1
        if keys[pygame.K_j]:
            target_frame -= searchspeed
        if keys[pygame.K_l]:
            target_frame += searchspeed

        # key input for fast forward : >
        if keys[pygame.K_PERIOD]:
            if targetms > 1:
                targetms -= 1
        # key input for slomo : <
        if keys[pygame.K_COMMA]:
            if targetms < 1000:
                targetms += 1

        # faster & slower point movements for each user

        if keys[pygame.K_LSHIFT]:
            if lms > 2:
                lms -= 1
        if keys[pygame.K_LCTRL]:
            if lms < 100:
                lms += 1
        if keys[pygame.K_RSHIFT]:
            if rms > 2:
                rms -= 1
        if keys[pygame.K_RCTRL]:
            if rms < 100:
                rms += 1

        # cut out selected box
        if keys[pygame.K_x]:
            crop = True
            mask = False

        # change color
        if keys[pygame.K_c] and not pressed:
            idx = (idx + 1)%8
            binary = "{0:b}".format(idx).zfill(3)
            color = tuple([int(x)*255 for x in binary])
            box_color = '#%02x%02x%02x' % color
            pressed = True
        elif not keys[pygame.K_c]:
            pressed = False

        # place colorbox
        if keys[pygame.K_v]:
            color = (255, 255, 255)
            mask = True
            crop = False

        loopms += tick
        if pause:
            # color = (255, 0, 0)
            if target_frame != cap.get(cv2.CAP_PROP_POS_FRAMES)-1:
                if target_frame > 0 and target_frame < totalFrames:
                    # set frame position
                    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                    success, frame = cap.read()
                    if not success:
                        break
        else:
            if loopms >= targetms:
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                success, frame = cap.read()
                if not success:
                    break
                loopms = 0

        if mask:
            cap.release()
            cv2.destroyAllWindows()
            subprocess.call(f'ffmpeg -y -i {videodir} -vf "drawbox=x={x1-1}:y={y1-1}:w={x2-x1+3}:h={y2-y1+3}:color={box_color}@1:t=fill" -c:a copy {outputdir+"_mask.mp4"}', shell=True)
            break



        elif crop:
            cap.release()
            cv2.destroyAllWindows()
            width, height = x2-x1+3, y2-y1+3
            width = width-width%4
            height = height-height%4
            subprocess.call(f'ffmpeg -y -i {videodir} -vf "crop={width}:{height}:{x1-1}:{y1-1}" -c:a copy {outputdir+"_crop.mp4"}')
            break


        # make copy of original video frame
        disp = frame.copy()

        # disp + rect to video on pygameaw
        line_thickness = 2
        cv2.rectangle(disp, (x1, y1), (x2, y2), color, line_thickness)

        # cv2.rectangle(disp, (nx1, ny1), (nx2, ny2), (0, 0, 0), 2)

        video_surf = pygame.image.frombuffer(
            disp.tobytes(), disp.shape[1::-1], "BGR")
        win.blit(video_surf, (0, 0))
        pygame.display.flip()
        pygame.display.update()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

