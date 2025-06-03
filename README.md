
# **Classification and Detection of Metals**
This repository contains the implementation for metal detection and classification from images, using computer vision and machine learning.

## There are *4 steps* for this project 🔍:
- Edge Detection
- Segmentation
- Classification
- Sending Coordinates for Real World Use

> Out of these, ony first one step(s) are implemented so far. 🤔
---
 
## Before Continuing Reading 📖
To contribute to this project, you need to have a tensorflow gpu environment using Ananconda
> The tutorial link for setting up a tensorflow gpu environment using anaconda is [here](https://youtu.be/QUjtDIalh0k?si=g_FBCRnNLLYPU-_F)
All following sections will assume you have this step already done ✔️.
 
---

# I: Edge Detection
- Divide image into 50x50 grid.
- Label the grid cells as ```1``` if edge exists in grid cell, ```0``` otherwise.
- Take the fourier transform for each grid cell in-place.
- Final image with label:
- ![Labelled Image for Edge Detection](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/edge_detection_labelled_image.png)

## We feed the new labels and images to the CNN
> The architecture of the CNN can be viewed in ```MetalEdge.ipynb```
### Training Loss
