
# **Classification and Detection of Metals**
This repository contains the implementation for metal detection and classification from images, using computer vision, and machine learning.

## There are *4 steps* for this project 🔍:
- Edge Detection
- Segmentation
- Classification
- Sending Coordinates for Real World Use

> Out of these, only first one step(s) are implemented so far. 🤔
---
 
## Before Continuing Reading 📖
To contribute to this project, you need to have a tensorflow gpu environment using Ananconda
> The tutorial link for setting up a tensorflow gpu environment using anaconda is [here](https://youtu.be/QUjtDIalh0k?si=g_FBCRnNLLYPU-_F).
All following sections will assume you have this step already done ✔️.
 
---

# I: Edge Detection 🕵️
- Divide image into 50x50 grid.
- Label the grid cells as ```1``` if edge exists in grid cell, ```0``` otherwise (refer ```edge_annotator.py```).
- Take the fourier transform for each grid cell in-place.

  Final image with label:

  ![Labelled Image for Edge Detection](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/edge_detection_labelled_image.png)

## We Feed the New Labels and Images to the CNN
> The architecture of the CNN can be viewed in ```MetalEdge.ipynb```
Use ```ds_maker.py``` to make a tensorflow dataset from the annotated images to train CNN.
### Training Loss 📉
![Smoothed Training Loss Curve](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/edge_detection/results/smoothed_training_loss.png)
### Prediction Results
![Prediction Result](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/edge_detection/results/test_results_1.png)

***NOTE: More data is needed for edge detection, so if anyone wants to collect image and annotate, feel free to do so.***

---

# II: Segmentation 📝
Given the image with now the detected labels, we must now segment all enclosed areas.

Now, since we have divided the image into a 50x50 grid, and each grid cell can either be an edge or not an edge, (refer prediction results, you can clearly see that the image has been divided into a 50x50 grid, and that if any grid cell contains an edge it is marked with the red colour), we can now run the connected components algorithm on the remaining grid cells to segment it.

This will simplify the task from running the connected components algorithm on the original image on all the pixels.

## Consider the following image:

![](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/snippet.png)

We see a snippet of the 50x50 grid, with the cells that contains an edge being marked as red. We see the edge divides the image into two components, one component to the left, the other to the right. Thus, after running [connected components algorithm](https://www.geeksforgeeks.org/connected-components-in-an-undirected-graph/) (using [4 adjacency neighbourhood](https://www.imageprocessingplace.com/downloads_V3/root_downloads/tutorials/contour_tracing_Abeer_George_Ghuneim/connectivity.html)), the image now is labeled as such:

## Image with labelled regions:

![](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/labelled_snippet.png)

> Where, R means 'Region'.
## Now we segment and save all the regions in the image.

![](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/region_one.png)

![](https://github.com/AgiGames/MetalDetectAndClassify/blob/main/readme_stuff/region_two.png)

We repeat this for all other regions that may exist in the image.
