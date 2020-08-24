import cv2


# Functions

def resize(img, k):
    height, width = img.shape[:2]
    img = cv2.resize(img, (int(width / k), int(height / k)), cv2.INTER_CUBIC)
    return img


# Tries to avoid collisions and moves away from it in the most smooth way (Because The square_man can fly a little)
def escape_from_collision(fgmask, object, stuck, current_x, current_y):
    if (stuck == 0):
        return (current_x, current_y)
    jump_length = 1
    while (jump_length < 200):
        y_options = (current_y, current_y + jump_length, current_y - jump_length)
        x_options = (current_x, current_x + jump_length, current_x - jump_length)

        for y in y_options:
            for x in x_options:
                i = x
                stk = 0
                while (i < min(x + square_man.shape[1], frame.shape[1])):
                    j = y
                    if (stk == 1):
                        break
                    while (j < min(y + square_man.shape[0], frame.shape[0])):
                        if (x < 0):
                            if (fgmask[j, 0] != 0):
                                stk = 1
                                break
                        if (y < 0):
                            if (fgmask[0, i] != 0):
                                stk = 1
                                break
                        if (fgmask[j, i] != 0):
                            stk = 1
                            break
                        j = j + 8
                    i = i + 8
                if (stk == 0):
                    return (x, y)
        if (jump_length < 40):
            jump_length = jump_length + 1;
        else:
            jump_length = jump_length + 50;
    return (current_x, current_y)


recording = 0
saved_video_counter = 0;
saved_image_counter = 0;
square_man_regular = cv2.imread("bird.jpg")
square_man_regular = resize(square_man_regular, 2)
square_man = square_man_regular
score = 0;
in_movement = 0
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

cap = cv2.VideoCapture(0)

# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
fgbg = cv2.createBackgroundSubtractorMOG2()

x = 300
y = -square_man.shape[0] + 3
ret, frame = cap.read()

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# video_name = "video" + str(saved_video_counter) + ".avi"
# out = cv2.VideoWriter(video_name, fourcc, 20.0, (frame.shape[1], frame.shape[0]))

square_man_x2 = min((frame.shape[1] - x), square_man.shape[1])
square_man_y2 = min((frame.shape[0] - y), square_man.shape[0])
y_offset = max(y, 0)
x_offset = max(x, 0)
square_man_height = max(square_man_y2 - max(0, -y), 0)
square_man_width = max(square_man_x2 - max(0, -x), 0)
while True:
    ret, frame = cap.read()
    fgmask = fgbg.apply(frame)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    f = frame.copy()
    stuck = 0
    if ((y < (frame.shape[0] - 1)) and (x < (frame.shape[1] - 1)) and ((y + square_man.shape[0]) > 1) and (
            (x + square_man.shape[1]) > 1) and (square_man_width > 0) and (square_man_height > 0)):
        i = x
        while (i < min(x + square_man.shape[1], frame.shape[1])):
            j = y
            if (stuck == 1):
                break
            while (j < min(y + square_man.shape[0], frame.shape[0])):
                if (x < 0):
                    if (fgmask[j, 0] != 0):
                        stuck = 1
                        break
                if (y < 0):
                    if (fgmask[0, i] != 0):
                        stuck = 1
                        break
                if (fgmask[j, i] != 0):
                    stuck = 1
                    break
                j = j + 5
            i = i + 5
        square_man_x2 = min((frame.shape[1] - x), square_man.shape[1])
        square_man_y2 = min((frame.shape[0] - y), square_man.shape[0])
        y_offset = max(y, 0);
        x_offset = max(x, 0);
        square_man_height = max(square_man_y2 - max(0, -y), 0)
        square_man_width = max(square_man_x2 - max(0, -x), 0)
        frame[y_offset:y_offset + square_man_height, x_offset:x_offset + square_man_width] = square_man[
                                                                                             max(0, -y):max(0,
                                                                                                            -y) + square_man_height,
                                                                                             max(0, -x):max(0,
                                                                                                            -x) + square_man_width]
        (x, y) = escape_from_collision(fgmask, square_man, stuck, x, y)

    else:
        if (y < 0):
            score = score + 5
        elif (y < frame.shape[0] - 1):
            score = score + 1

        x = 300
        y = -square_man.shape[0] + 3
    if stuck == 0:
        y = y + 4
    font = cv2.FONT_HERSHEY_SIMPLEX
    frame = cv2.flip(frame, 1)

    cv2.putText(frame, 'score: ' + str(score), (40, 40), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Mask', fgmask)
    cv2.imshow('Interactive Webcam Game', frame)
    k = cv2.waitKey(30) & 0xff

    if k == 27:
        break
    elif k % 256 == 32:  # space key pressed
        img_name = "image_{}.jpg".format(saved_image_counter)
        cv2.imwrite(img_name, frame)
        saved_image_counter = saved_image_counter + 1
    # elif k % 256 == 82: # R key pressed
    #     recording = True
    # elif k % 256 == 80: # P key pressed
    #     recording = False
    # if recording:
    #     out.write(f)

cap.release()
# out.release()
cv2.destroyAllWindows()
