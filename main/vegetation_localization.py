import cv2
import numpy as np
from django.conf import settings


def veg_localization(img_, img_name):
    # reading the image
    img = cv2.imread(img_)

    # converting image from RGB to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # setting threshold value to detect green parts of the image
    threshold = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))

    # for only green color
    '''
    imask = threshold > 0
    green = np.zeros_like(img, np.uint8)
    green[imask] = img[imask]
    '''

    # for naming convention
    img_name = img_name.split('.')

    output_path = 'output/' + img_name[0] + '_Output.' + img_name[1]
    cv2.imwrite(settings.BASE_DIR + settings.MEDIA_URL + output_path, threshold)

    return output_path
