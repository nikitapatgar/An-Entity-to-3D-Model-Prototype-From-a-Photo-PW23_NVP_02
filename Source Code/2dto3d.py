import os
import numpy as np
from PIL import Image, ImageOps
from stl import mesh
import face_recognition
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def create_stl(x, y, z, output_folder, filename, height_factor=2):
  z_scaled = np.clip(z * height_factor, a_min=None, a_max=z.max())
  faces = []
  for i in range(x.shape[0] - 1):
    for j in range(x.shape[1] - 1):
      z_idx = lambda i, j: i * y.shape[1] + j
      faces.append([z_idx(i, j), z_idx(i + 1, j), z_idx(i + 1, j + 1)])
      faces.append([z_idx(i, j), z_idx(i + 1, j + 1), z_idx(i, j + 1)])

  vertices = np.column_stack((x.ravel(), y.ravel(), z_scaled.ravel()))
  face_array = np.zeros(len(faces), dtype=mesh.Mesh.dtype)
  for i, f in enumerate(faces):
    for j in range(3):
      face_array['vectors'][i][j] = vertices[f[j], :]

  model_mesh = mesh.Mesh(face_array)
  model_mesh.save(os.path.join(output_folder, f'{filename}.stl'))


def main1():
  image_path = "/Users/titeershaghatakchowdhury/Desktop/final/uploads/nikita_3.jpg"
  output_folder = "/Users/titeershaghatakchowdhury/Desktop/final/output"
  os.makedirs(output_folder, exist_ok=True)

  image = Image.open(image_path).convert('L')
  image = ImageOps.autocontrast(image)

  face_locations = face_recognition.face_locations(np.array(image))
  if face_locations:
    top, right, bottom, left = face_locations[0]
    face_image = image.crop((left, top, right, bottom))
    image_array = np.array(face_image)
  else:
    raise Exception("No face found in image.")

  nose_center = (face_image.size[0] // 2, face_image.size[1] // 2)
  y, x = np.ogrid[:image_array.shape[0], :image_array.shape[1]]
  x, y = np.meshgrid(x - nose_center[0], y - nose_center[1])

  create_stl(x, y, image_array, output_folder, '3d_stl', height_factor=0.3)

  # Function to simulate the rotation of the 3D plot around the x-axis
  def rotate(ax, angle):
    ax.view_init(elev=angle, azim=0)  # Rotate around the x-axis

  # Load the image and convert it to grayscale
  image = Image.open(
      "/Users/titeershaghatakchowdhury/Desktop/final/uploads/nikita_3.jpg"
  ).convert('L')
  image_array = np.array(image)

  # Find the nose center, assuming it is at the center of the image
  nose_center = (image_array.shape[1] // 2, image_array.shape[0] // 2)

  # Find the base of the neck (assuming it is at the bottom of the image)
  neck_base = image_array.shape[0]

  # Create x and y coordinates with the nose as the middle point
  x = np.arange(image_array.shape[1])
  y = np.arange(
      neck_base)  # y coordinates from the top to the base of the neck
  x, y = np.meshgrid(x - nose_center[0], y - nose_center[1])

  # Use the pixel values as z-coordinates and scale the depth by 0.05 (reduced depth scaling)
  z = image_array * 0.025

  # Create the figure and axis for the plot in 3D with increased size
  fig = plt.figure(figsize=(8, 6))
  ax = fig.add_subplot(111, projection='3d')

  # Set up the folder for saving images
  output_folder = "/Users/titeershaghatakchowdhury/Desktop/final/output"
  os.makedirs(output_folder, exist_ok=True)

  # Plot the surface with improved quality settings
  surf = ax.plot_surface(x,
                         y,
                         z,
                         rstride=1,
                         cstride=1,
                         cmap=plt.cm.gray,
                         linewidth=0,
                         antialiased=True,
                         shade=True)

  # Rotate and capture images at 15-degree intervals around the x-axis up to 90 degrees
  for angle in range(-90, 91, 15):
    rotate(ax, angle)
    filename = os.path.join(output_folder, f'rotation_{angle}.png')
    plt.savefig(filename, dpi=1200)  # Save with higher resolution

  # Save the 3D model with increased dpi
  model_filename = os.path.join(output_folder, '3D_model.png')
  plt.savefig(model_filename, dpi=1200)  # Save with higher resolution
  plt.show()


if __name__ == "__main__":
  main1()
