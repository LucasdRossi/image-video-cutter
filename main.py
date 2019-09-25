from argparse import ArgumentParser
import numpy as np
from cv2 import cv2


def build_args():
    parser = ArgumentParser()
    parser.add_argument("-img", "--image_path", required=False,
                        type=str, help="path to the image", default="./resources/image.jpg")
    parser.add_argument("-v", "--video", required=False,
                        type=str, help="type CAM to webcam or the path to the video", default=None)
    return parser


def get_mouse_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points = (x, y)
        all_points.append(points)
        cv2.circle(img_copy, points, 5, (0, 0, 255), 2)


def get_points():
    min_x = all_points[0][0]
    max_x = all_points[0][0]
    min_y = all_points[1][1]
    max_y = all_points[1][1]
    for points in all_points:
        if points[0] < min_x:
            min_x = points[0]
        if points[0] > max_x:
            max_x = points[0]
        if points[1] > max_y:
            max_y = points[1]
        if points[1] < min_y:
            min_y = points[1]

    return min_x, max_y, max_x, min_y


def get_final_img():
    min_x, max_y, max_x, min_y = get_points()
    square_img = img[min_y:max_y, min_x:max_x]

    mask = np.zeros(square_img.shape, square_img.dtype)
    cv2.fillPoly(
        img_to_cut, [np.asarray(all_points, dtype=np.int32)], (255, 255, 255))
    mask = img_to_cut[min_y:max_y, min_x:max_x]
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    final = cv2.bitwise_and(square_img, mask)
    return final


if __name__ == '__main__':
    all_points = []
    args = build_args().parse_args()
    selecting_points = False
    selected_points = False
    cropped_img = False
    get_frame = True
    video = True if args.video != None else False

    if video:
        if args.video == 'CAM':
            cam = cv2.VideoCapture(0)
        else:
            cam = cv2.VideoCapture(args.video)
    else:
        img_path = args.image_path
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img_copy = img.copy()
        img_to_cut = img.copy()

    while True:
        if video:
            _, img = cam.read()
            img_to_cut = img.copy()

        cv2.imshow('image', img)
        key = cv2.waitKey(100)

        if key == 115:  # 's'
            cv2.namedWindow('select points')
            cv2.setMouseCallback('select points', get_mouse_points)
            selecting_points = True

        if selecting_points:
            if get_frame and video:
                img_copy = img.copy()
                get_frame = False
            cv2.imshow('select points', img_copy)

        if key == 99 and len(all_points) > 2 and selecting_points:  # 'c'
            selected_points = True
            selecting_points = False
            cv2.setMouseCallback(
                'select points', lambda event, x, y, flags, param: None)

        if selected_points:
            final_img = get_final_img()
            cropped_img = True
            if not video:
                selected_points = False

        if cropped_img:
            cv2.imshow('cropped image', final_img)
            if not video:
                cropped_img = False

        if key == 113:  # 'q'
            if video:
                cam.release()
            cv2.destroyAllWindows()
            break
