# FaceLandmarkTrainer
A simple Dlib's face landmark model trainer.
If you have no idea what's this, you can refer to [this tutorial](https://www.pyimagesearch.com/2017/04/03/facial-landmarks-dlib-opencv-python/).

# Basic
**$ python marker.py [dir]**
<br>[dir] is the directory of your images

If it's the first time to mark, you need to input the name of your dataset and comment(optional).
Else, it will load the XML file. And create a backup file.

# How to mark
When a photo is loaded, you need first click two point (start, stop) to draw a rectangle of the face.
Then, you need to add 68 points to the face.

# Keyboard Control
- **ESC**: save and exit
- **Up**: Go to the last photo not finish
- **Down**: Go to the next not finish photo
- **Left**: Go to the previous photo
- **Right**: Go to the next photo
- **R**: Remove the box attribute, say rectangle
- **Backspace**: Delete the last part
