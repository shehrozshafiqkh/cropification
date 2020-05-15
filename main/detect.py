import numpy as np
import argparse
import time
import cv2
import os
from django.conf import settings

confthres = 0.5
nmsthres = 0.1
Areas = {}
Parameter_width = {}
Parameter_height = {}

def get_labels(labels_path):
    # load the COCO class labels our YOLO model was trained on
    lpath = os.path.sep.join([labels_path])
    LABELS = open(lpath).read().strip().split("\n")
    print(LABELS)
    
    for key in LABELS:
        Areas[key] = 0
        Parameter_width[key] = 0
        Parameter_height[key] = 0
    
    return LABELS


def get_colors(LABELS):
    # initialize a list of colors to represent each possible class label
    np.random.seed(42)
    COLORS = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255),
              (255, 0, 255), (255, 255, 0), (255, 255, 255)]
    return COLORS


def get_weights(weights_path):
    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([weights_path])
    return weightsPath


def get_config(config_path):
    configPath = os.path.sep.join([config_path])
    return configPath


def load_model(configpath, weightspath):
    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    return net


def get_prediction(image, net, LABELS, COLORS):
    (H, W) = image.shape[:2]

    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    #print(layerOutputs)
    end = time.time()

    # show timing information on YOLO
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            # print(scores)
            classID = np.argmax(scores)
            # print(classID)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > confthres:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                            nmsthres)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # draw a bounding box rectangle and label on the image
            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 10)
            text = "{}: {:.2f}".format(LABELS[classIDs[i]], confidences[i] * 100)
            #print(boxes)
            #print(classIDs)
            
            temp = Areas[LABELS[classIDs[i]]]
            temp2 = Parameter_width[LABELS[classIDs[i]]]
            temp3 = Parameter_height[LABELS[classIDs[i]]]
            
            # 1 pixel is equal to 2.66 cm
            Areas[LABELS[classIDs[i]]] = (((w * 2.66) * (h * 2.66)) * 0.00107639) + temp
            Parameter_width[LABELS[1]] = w + temp2
            Parameter_height[LABELS[1]] = h + temp3
            
            cv2.putText(image, text, (x, y - 15),cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 5)
    return image


def main_detect(img_, img_name):
    image = cv2.imread(img_)
    labelsPath = "yolo_v3/obj.names"
    cfgpath = "yolo_v3/yolov3.cfg"
    wpath = "yolo_v3/yolov3_6000.weights"

    labelsPath = os.path.join(
        settings.BASE_DIR, labelsPath).replace(os.sep, '/')
    cfgpath = os.path.join(settings.BASE_DIR, cfgpath).replace(os.sep, '/')
    wpath = os.path.join(settings.BASE_DIR, wpath).replace(os.sep, '/')

    Lables = get_labels(labelsPath)
    CFG = get_config(cfgpath)
    Weights = get_weights(wpath)
    nets = load_model(CFG, Weights)
    Colors = get_colors(Lables)

    res = get_prediction(image, nets, Lables, Colors)

    img_name = img_name.split('.')

    output_path = 'output/' + img_name[0] + '_Output.' + img_name[1]
    cv2.imwrite(settings.BASE_DIR + settings.MEDIA_URL + output_path, res)
    return output_path, Areas, Parameter_width, Parameter_height
