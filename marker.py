#!/usr/bin/python

# This program is made for manually mark points for shape predictors, and generate a XML file.
# The generated XML's structure is same as sample.xml in the same folder.
# You need to provide directory for photos as arg[1]
# If the result XML already exist, it will load data, then append to it
# Made by Eysure github.com/eysure
# # Jul 2, 2018

import cv2
import os
import sys
import shutil
import datetime
from lxml import etree

ENCODING = "ISO-8859-1"
NUM_POINT = 68
DIRECTORY = os.path.join(os.getcwd(), "sample")
FILENAME = os.path.join(DIRECTORY, "result.xml")
root = None


def save():
    xml_file = open(FILENAME, "w")
    xml_file.write(etree.tostring(root, pretty_print=True, encoding=ENCODING).decode(ENCODING))
    xml_file.close()


def delete_unused_node():
    print("\nCleaning unused node...")
    counter = 0
    for img in images:
        rel_path = img.attrib['file']
        if not os.path.isfile(os.path.join(DIRECTORY, rel_path)):
            images.remove(img)
            print("Delete: ", rel_path)
            counter += 1
    if counter == 0:
        print("No node is redundant.")
    else:
        print(counter, "node(s) deleted")


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        this_box = param["box"]

        # Get and compute to object's coordinate
        fx = round(x / param['scale_rate'])
        fy = round(y / param['scale_rate'])
        ix = round(fx * float(param['scale_rate']))
        iy = round(fy * float(param['scale_rate']))

        if 'top' not in this_box.attrib or 'left' not in this_box.attrib:
            this_box.attrib['top'] = str(fy)
            this_box.attrib['left'] = str(fx)
            cv2.circle(mat, (ix, iy), 3, (0, 255, 0))
            cv2.imshow(param["rel_path"], mat)
        elif 'width' not in this_box.attrib or 'height' not in this_box.attrib:
            this_box.attrib['width'] = str(fx - int(this_box.attrib['left']))
            this_box.attrib['height'] = str(fy - int(this_box.attrib['top']))
            cv2.rectangle(mat, (int(int(this_box.attrib['left']) * float(param['scale_rate'])),
                                int(int(this_box.attrib['top']) * float(param['scale_rate']))), (ix, iy), (0, 255, 0),
                          2)
            cv2.imshow(param["rel_path"], mat)
        else:
            if len(this_box) >= NUM_POINT:
                print("Max points.")
                return False

            # Add to XML tree
            part = etree.Element("part")
            if len(this_box) < 10:
                part.attrib['name'] = '0' + str(len(this_box))
            else:
                part.attrib['name'] = str(len(this_box))

            part.attrib['x'] = str(fx)
            part.attrib['y'] = str(fy)
            this_box.append(part)

            # Draw point

            cv2.circle(mat, (ix, iy), 3, (0, 0, 255))
            cv2.putText(mat, str(part.attrib['name']), (ix, iy), cv2.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 1,
                        cv2.LINE_AA)
            cv2.imshow(param["rel_path"], mat)


def is_photo_marked(index):
    image = images[index]
    box = image.find("box")
    if box is not None and 'top' in box.attrib and 'left' in box.attrib:
        if 'width' in box.attrib and 'height' in box.attrib:
            if len(box) == NUM_POINT:
                return True
    return False


def find_unmark_photo(direction, i, image_count):
    if direction:
        for index in range(i + 1, image_count - 1):
            if not is_photo_marked(index):
                return index
        print("No unmarked photo after")
        return i
    else:
        for index in range(i - 1, 0, -1):
            if not is_photo_marked(index):
                return index
        print("No unmarked photo before")
        return i


# OpenCV debug
print("OpenCV version: {}".format(cv2.__version__))

# Assign global argv
if len(sys.argv) >= 2 and sys.argv[1]:
    DIRECTORY = sys.argv[1]
    FILENAME = os.path.join(DIRECTORY, "result.xml")

print("Img directory: " + DIRECTORY)
print("XML file name: " + FILENAME)

# Check if file is exist
if os.path.isfile(FILENAME):
    # Make backup first
    now = datetime.datetime.now()
    shutil.copyfile(FILENAME, FILENAME + "." + str(now) + ".bak")

    f = open(FILENAME, "r")
    try:
        root = etree.parse(f)
    except etree.Error:
        print("Error, Bad XML file. Parse failed.")
        exit(4)
    print("XML File read successfully")
    images = root.find("images")
    delete_unused_node()
elif os.path.isdir(DIRECTORY):
    print("New XML File")

    # Initialize
    root = etree.Element('dataset')
    name = etree.Element('name')
    name.text = input("Please input the dataset name: ")
    root.append(name)
    comment = etree.Element('comment')
    comment.text = input("Please input comment (Optional): ")
    if comment.text:
        root.append(comment)
    root.append(etree.Element('images'))
    save()
    images = root.find("images")
else:
    print("\nNo valid directory found.")
    print("You need to provide an valid directory as argument of this program, such as")
    print("\t $ python marker.py ~/Document/photos")
    print("I can't do anything without it. :(")
    exit(500)

# From there on, we only focus on <images>...</images> node
mat = None

# Traverse images in folders via os.walk
print("\nTraversing image folder...")
for path, dirs, files in os.walk(DIRECTORY):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(path, file)
            rel_path = os.path.relpath(full_path, DIRECTORY)
            image = images.xpath("//image[@file='" + rel_path + "']")
            if len(image) == 0:
                image = etree.Element('image', file=rel_path)
                images.append(image)
                print("Add: '" + rel_path + "'.")
            else:
                print("Exist: '" + rel_path + "'.")

# Start to iterate
image_count = len(images)
exit_key = False
i = 0
i_change_flag = True

while not exit_key:
    image = images[i]
    rel_path = image.attrib['file']
    full_path = os.path.join(DIRECTORY, rel_path)
    mat = cv2.imread(full_path)
    height, width = mat.shape[:2]
    scale_rate = 720 / height
    mat = cv2.resize(mat, (0, 0), fx=scale_rate, fy=scale_rate)
    cv2.imshow(rel_path, mat)

    if is_photo_marked(i):
        print("☑ [", str(i + 1) + "/" + str(image_count), "]", rel_path)
    else:
        print("☐ [", str(i + 1) + "/" + str(image_count), "]", rel_path)

    # Load points (NOTICE THAT THIS IS ONLY SINGLE BOX SUPPORTED)
    box = image.find("box")

    # New box
    if box is None:
        print("New box for ", rel_path)
        box = etree.Element("box")
        image.append(box)

    # Draw box rectangle
    if 'top' in box.attrib and 'left' in box.attrib and 'width' in box.attrib and 'height' in box.attrib:
        cv2.rectangle(mat,
                      (int(int(box.attrib['left']) * scale_rate),
                       int(int(box.attrib['top']) * scale_rate)),
                      (int((int(box.attrib['left']) + int(box.attrib['width'])) * scale_rate),
                       int((int(box.attrib['top']) + int(box.attrib['height'])) * scale_rate)),
                      (0, 255, 0), 2)
        cv2.imshow(rel_path, mat)

    # Draw every part in box
    for part in box:
        ix = round(int(part.attrib['x']) * scale_rate)
        iy = round(int(part.attrib['y']) * scale_rate)
        cv2.circle(mat, (ix, iy), 3, (0, 0, 255))
        cv2.putText(mat, str(part.attrib['name']), (ix, iy), cv2.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.imshow(rel_path, mat)

    cv2.setMouseCallback(rel_path, mouse_callback,
                         param={"rel_path": rel_path, "box": box, "scale_rate": scale_rate})

    # Key control
    # KEY ESC: save and exit
    key = cv2.waitKey()
    if key == 27:
        exit_key = True

    # KEY Up: Go to the last photo not finish
    elif key == 0:
        save()
        if i == 0:
            print("It's the first image")
        else:
            i = find_unmark_photo(False, i, image_count)
    # KEY Down: Go to the next not finish photo
    elif key == 1:
        save()
        if i < image_count - 1:
            i = find_unmark_photo(True, i, image_count)
        else:
            print("It's the last image")

    # KEY Left: Go to the previous photo
    elif key == 2:
        save()
        if i == 0:
            print("It's the first image")
        else:
            i -= 1

    # KEY Right: Go to the next photo
    elif key == 3:
        save()
        if i < image_count - 1:
            i += 1
        else:
            print("It's the last image")

    # KEY R: Remove the box attribute, say rectangle
    elif key == 114:
        box.attrib.clear()
        print("Box attrib removed.")

    # KEY Backspace: Delete the last part
    elif key == 127:
        if len(box) > 0:
            if len(box) - 1 < 10:
                name = '0' + str(len(box) - 1)
            else:
                name = str(len(box) - 1)
            part_to_delete = box.xpath("part[@name='" + name + "']")[0]
            box.remove(part_to_delete)
        else:
            print("No point remain.")
    # Other key will reset this image

    cv2.destroyAllWindows()
