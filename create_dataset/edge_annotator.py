import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import uuid

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

        # we add 3 action listeners for drawing lines (start drawing, while drawing, end drawing)
        self.canvas.bind("<Button-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        # self.canvas.bind("<ButtonRelease-1>", self.end_line)

        # contains all coordinates of the lines
        self.line_coords = []

        # add an action listener for enter button which when pressed will load the next image to canvas
        self.root.bind("<Return>", lambda event: self.load_next_image_to_canvas())

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

    def draw_line(self, event):

        # add the new coordinate to the line coords
        self.line_coords.append((event.x, event.y))
        previous_coordinate = self.line_coords[-2]
        current_coodinate = self.line_coords[-1]

        # draw line from previous coordinate to current coordinate
        self.canvas.create_line(previous_coordinate[0], previous_coordinate[1], current_coodinate[0], current_coodinate[1], fill="red", width=1)

    def segment_and_save(self):
        
        # create pop up notification
        popup = tk.Toplevel(self.root)
        popup.title("Status")
        popup.geometry("200x100+400+300")  # Small centered window
        label = tk.Label(popup, text="Segmenting...", font=("Arial", 12))
        label.pack(expand=True)

        # force window to draw the popup now (before long task starts)
        self.root.update()

        # get the directories where images and labels will be saved
        image_dir = os.path.join(tfds_storage_directory, "images")
        label_dir = os.path.join(tfds_storage_directory, "labels")

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

                # crop out the grid cell to save in the future
                patch = self.resized_image.crop((x_low, y_low, x_high, y_high)).resize((patch_size, patch_size))
                label = 0

                # now we must find, if the grid cell was marked as an edge or not
                # (if line was drawn on the grid cell or not)
                for coord in self.line_coords:
                    # if any line coordinate lies in the grid cell, then that grid cell is marked
                    # as edge
                    if x_low <= coord[0] and coord[0] < x_high and y_low <= coord[1] and coord[1] < y_high:
                        label = 1
                        break
                
                # get a unique id
                image_id = str(uuid.uuid4())
                
                # save the image with that id
                patch.save(os.path.join(image_dir, f"{image_id}.png"))

                # save the label with the same id (text file)
                label_path = os.path.join(label_dir, f"{image_id}.txt")
                with open(label_path, "w") as f:
                    f.write(str(label))
        
        # destroy the popup
        popup.destroy()

root = tk.Tk()
viewer = AnnotatorApp(root)
root.mainloop() # start the app
