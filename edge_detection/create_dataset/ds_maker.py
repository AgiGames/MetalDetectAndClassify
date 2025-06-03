import tensorflow as tf
import numpy as np
import os

def load_npy_label(label_path):

    label = np.load(label_path.decode('utf-8'))
    return label.astype(np.int32)

def load_sample(image_path, label_path):

    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [750, 750])

    label = tf.numpy_function(load_npy_label, [label_path], tf.int32)

    print(label)

    label.set_shape([50, 50])

    return image, label

IMG_DIR = "images"
LBL_DIR = "tfds_storage/labels"

image_paths = sorted([
    os.path.join(IMG_DIR, f) 
    for f in os.listdir(IMG_DIR) 
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])

label_paths = [
    p.replace('.png', '.npy').replace('.jpg', '.npy').replace('.jpeg', '.npy').replace(IMG_DIR, LBL_DIR) 
    for p in image_paths
]

ds = tf.data.Dataset.from_tensor_slices((image_paths, label_paths))
ds = ds.map(load_sample, num_parallel_calls=tf.data.AUTOTUNE)

ds.save("metal_edge_dataset_2")