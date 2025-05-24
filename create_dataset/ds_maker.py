import tensorflow as tf
import numpy as np
import os

def load_sample(image_path, label_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [250, 250])

    label_text = tf.io.read_file(label_path)
    label = tf.strings.to_number(tf.strings.strip(label_text), out_type=tf.int32)

    return image, label

IMG_DIR = "tfds_storage/images"
LBL_DIR = "tfds_storage/labels"

image_paths = sorted([os.path.join(IMG_DIR, f) for f in os.listdir(IMG_DIR) if f.endswith('.png')])
label_paths = [p.replace('.png', '.txt').replace(IMG_DIR, LBL_DIR) for p in image_paths]

ds = tf.data.Dataset.from_tensor_slices((image_paths, label_paths))
ds = ds.map(load_sample, num_parallel_calls=tf.data.AUTOTUNE)

ds.save("metal_edge_dataset")
