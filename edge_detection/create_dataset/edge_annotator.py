import os
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

num_grids = 50 # num grids per row (there will be 50 rows)
patch_size = 250 # the size to which each grid cell will be segmented and resized to
image_size = 750
tfds_storage_directory = "tfds_storage" # the folder where images and labels will be stored
images_directory = "images" # the folder where images will be fetched for annotation

# make this directories at the start just in case
os.makedirs(os.path.join(tfds_storage_directory, "images"), exist_ok=True)
os.makedirs(os.path.join(tfds_storage_directory, "labels"), exist_ok=True)

class AnnotatorApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Edge Annotator") # set title

        self.canvas = tk.Canvas(root, width=image_size, height=image_size) # canvas displays a 750x750 image, so set it's size to 750x750
        self.canvas.pack()

        # get the name of all images in the images directory and store them in the images_list
        self.image_list = [f for f in os.listdir(images_directory) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        # index of the current image to display on canvas
        self.current_image_index = 0

        self.original_image = None # original image fetched from folder to display
        self.resized_image = None
        self.displayed_image = None # image that will be displayed in the canvas (resized original image to 750x750)

        # load the 0th image to canvas
        self.load_image_to_canvas()

        # we add 2 action listeners for drawing lines (new line, continue line)
        self.canvas.bind("<Button-3>", self.start_line)
        self.canvas.bind("<Button-1>", self.draw_line)

        # contains all coordinates of the lines
        self.line_coords = []

        # add an action listener for enter button which when pressed will load the next image to canvas
        self.root.bind("<Return>", lambda event: self.load_next_image_to_canvas())

        self.line_ids = []  # to store canvas IDs for undoing
        self.line_segments = []  # to store coordinate pairs (x1, y1, x2, y2) for undo

        # action listener for undo (control + z)
        self.root.bind("<Control-z>", lambda event: self.undo_last_line())


    def load_image_to_canvas(self):

        # if we have already annotated all images
        if self.current_image_index >= len(self.image_list):
            # notify the user and close the app
            messagebox.showinfo("All Images Annotated", "Closing Application")
            print("All images annotated... closing application.")
            self.root.after(2000, self.root.destroy)
            return
        
        # image path of the current image
        image_path = os.path.join(images_directory, self.image_list[self.current_image_index])
        print("Loading Image:", image_path)

        # load the original image
        self.original_image = Image.open(image_path).convert("RGB")
        # resize to 750x750
        self.resized_image = self.original_image.resize((image_size, image_size), Image.BILINEAR)
        # ready the image to display on tk canvass
        self.displayed_image = ImageTk.PhotoImage(self.resized_image)

        # delete previous image
        self.canvas.delete("all")
        # display the image
        self.canvas.create_image(0, 0, anchor='nw', image=self.displayed_image)
        # draw the grid
        self.draw_grid_over_canvas()

        # if the annotation has just started
        if self.current_image_index == 0:
            # notify the user on how to use the app
            messagebox.showinfo("Controls", "Right Click -> New Line\nLeft Click -> Continue Line")
            print("All images annotated... closing application.")

    def load_next_image_to_canvas(self):

        # segment the current image based on annotation
        self.segment_and_save()

        # increment the current image pointer, since we need to load the next image
        self.current_image_index += 1
        self.load_image_to_canvas() # call the load image function
    
    def draw_grid_over_canvas(self):

        cell_size = image_size // 50

        for i in range(0, 51): # 0 to 50 lines each side
            coordinate = i * cell_size
            self.canvas.create_line(coordinate, 0, coordinate, image_size, fill="blue", width=1)
            self.canvas.create_line(0, coordinate, image_size, coordinate, fill="blue", width=1)

    def start_line(self, event):
        
        # add the start of the line coordinate to line coords
        self.line_coords.append((event.x, event.y))

    # Bresenham line drawing algorithm
    # algorithm to draw line between two points (you can ignore this, unless you are interested in how the algorithm works)
    def bresenham_line(self, x1, y1, x2, y2):
        points = []

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1

        sx = 1 if x2 > x1 else -1
        sy = 1 if y2 > y1 else -1

        if dy <= dx:
            err = dx // 2
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
            points.append((x2, y2))
        else:
            err = dy // 2
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
            points.append((x2, y2))

        return points

    def draw_line(self, event):

        # get the current x and y coordinate
        curr = (event.x, event.y)

        # if no previous point exists to draw line from
        if len(self.line_coords) < 1:
            return # get out of function

        # get the previous coordinate
        prev = self.line_coords[-1]

        # initialize some variables (points using which the new line will be drawn)
        x1, y1 = prev
        x2, y2 = curr

        # draw line and get the coordinates that belong to the line
        coords_to_add = self.bresenham_line(x1, y1, x2, y2)

        # add the new coordinates of the line to line coords
        self.line_coords.extend(coords_to_add)

        # add new line segment points to line segments lists
        self.line_segments.append((x1, y1, x2, y2))  # Store full segment for undo

        # create the new line on the canvas for visibility
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill="red", width=1, tags="line")

        # append the new line id to line ids
        self.line_ids.append(line_id)

        # # debug print
        # print(self.line_coords)

    def undo_last_line(self):

        if not self.line_ids:
            return

        # remove last drawn line from canvas
        last_id = self.line_ids.pop()
        self.canvas.delete(last_id)

        # remove the last segment from line coords
        if self.line_segments:
            x1, y1, x2, y2 = self.line_segments.pop()

            # use bresenham to reconstruct which points were added
            coords_removed = self.bresenham_line(x1, y1, x2, y2)

            # remove these coords from line coords
            self.line_coords = self.line_coords[:-len(coords_removed)]

    def segment_and_save(self):
        
        # create pop up notification
        popup = tk.Toplevel(self.root)
        popup.title("Status")
        popup.geometry("200x100+400+300")  # Small centered window
        popup_label = tk.Label(popup, text="Segmenting...", font=("Arial", 12))
        popup_label.pack(expand=True)

        # force window to draw the popup now (before long task starts)
        self.root.update()

        # get the directories where images and labels will be saved
        image_dir = os.path.join(tfds_storage_directory, "images")
        label_dir = os.path.join(tfds_storage_directory, "labels")

        # create two arrays that stores the label and image
        label_array = [[0] * num_grids for _ in range(num_grids)]
        image_array = [[0] * image_size for _ in range(image_size)]

        # size of a single cell
        cell_size = image_size // 50

        # iterate through each grid
        for i in range(num_grids):
            for j in range(num_grids):
                
                '''
                x_low -> lowest x coordinate possible on that specific grid cell
                x_high -> highest x coordinate possible on that specific grid cell
                y_low -> lowest y coordinate possible on that specific grid cell
                y_high ->  highest y coordinate possible on that specific grid cell
                '''
                x_low = i * cell_size
                x_high = i * cell_size + cell_size

                y_low = j * cell_size
                y_high = j * cell_size + cell_size

                # crop out the grid cell to take the fourier transform
                patch = self.resized_image.crop((x_low, y_low, x_high, y_high))
                patch_array = np.array(patch.convert('L')) # convert to numpy array
                f_transform = np.fft.fft2(patch_array) # take fourier transform
                f_shifted = np.fft.fftshift(f_transform) # shift center of fourier transform to center
                magnitude_spectrum = np.log1p(np.abs(f_shifted)) # take log magnitude of fourier transform

                # normalize the magnitude
                normalized_spectrum = (255 * (magnitude_spectrum - np.min(magnitude_spectrum)) / 
                       (np.max(magnitude_spectrum) - np.min(magnitude_spectrum))).astype(np.uint8)

                # set the intensity value of the image to the intensity values of the normalized magnitude
                for k in range(x_low, x_high):
                    for l in range(y_low, y_high):
                        image_array[k][l] = normalized_spectrum[k - x_low][l - y_low]

                # now we must find, if the grid cell was marked as an edge or not
                # (if line was drawn on the grid cell or not)
                for coord in self.line_coords:
                    # if any line coordinate lies in the grid cell, then that grid cell is marked
                    # as edge
                    if x_low <= coord[0] and coord[0] < x_high and y_low <= coord[1] and coord[1] < y_high:
                        label_array[i][j] = 1
                        break
        
        # it was experimentally discovered (with astute difficulty) that these two lines are necessary for the label to
        # line up with the image, and I don't fucking know why
        label_array = np.flipud(label_array)
        label_array = np.rot90(label_array, k=3)
        
        # here aswell, image was rotated 90 degrees for some reason, so we bring it back to normal 🤡
        image_array = np.array(image_array).T

        fourier_image = Image.fromarray(image_array)
        # save the image with it's
        fourier_image.save(os.path.join(image_dir, f"{self.current_image_index}.png"))

        # save the label with the same id (npy file)
        np.save(os.path.join(label_dir, f"{self.current_image_index}.npy"), label_array)

        # since we are done with the current image, reset the lines and information regarding the lines
        self.line_coords = []
        self.line_ids = []
        self.line_segments = []

        # destroy the popup
        popup.destroy()

root = tk.Tk()
viewer = AnnotatorApp(root)
root.mainloop() # start the app