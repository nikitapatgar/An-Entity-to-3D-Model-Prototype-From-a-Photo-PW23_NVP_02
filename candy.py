import os
import numpy as np
from PIL import Image, ImageOps
from stl import mesh


# Functions from hero.py
def create_stl(x, y, z, output_folder, filename, height_factor=1):
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


def load_image_and_create_stl(image_path, output_folder, filename,
                              height_factor):
  image = Image.open(image_path).convert('L')
  image = ImageOps.autocontrast(image)
  image_array = np.array(image)

  y, x = np.ogrid[:image_array.shape[0], :image_array.shape[1]]
  x, y = np.meshgrid(x - image_array.shape[1] // 2,
                     y - image_array.shape[0] // 2)

  create_stl(x, y, image_array, output_folder, filename, height_factor)


def merge_stl(face_stl_path, bald_head_stl_path, output_path):
  face_mesh = mesh.Mesh.from_file(face_stl_path)
  bald_head_mesh = mesh.Mesh.from_file(bald_head_stl_path)

  min_face_z = np.min(face_mesh.z)
  max_bald_head_z = np.max(bald_head_mesh.z)
  height_offset = min_face_z - max_bald_head_z

  for i in range(len(bald_head_mesh.data)):
    bald_head_mesh.data['vectors'][i][:][:, 2] -= height_offset

  combined = mesh.Mesh(np.concatenate([face_mesh.data, bald_head_mesh.data]))
  combined.save(output_path)


def remove_non_face_edges_from_stl(stl_path, new_stl_path):
  original_mesh = mesh.Mesh.from_file(stl_path)
  normals = np.cross(original_mesh.vectors[:, 1] - original_mesh.vectors[:, 0],
                     original_mesh.vectors[:, 2] - original_mesh.vectors[:, 0])
  norms = np.linalg.norm(normals, axis=1)
  normals /= norms[:, None]
  mask = (normals != [1,0,0]).all(axis=1) & \
         (normals != [0,1,0]).all(axis=1) & \
         (normals != [0,0,1]).all(axis=1)
  new_vectors = original_mesh.vectors[mask, :, :]
  new_mesh = mesh.Mesh(np.zeros(len(new_vectors), dtype=mesh.Mesh.dtype))
  new_mesh.vectors = new_vectors
  new_mesh.save(new_stl_path)


# Functions from 7.py
def load_mesh(stl_path):
  return mesh.Mesh.from_file(stl_path)


def save_mesh(combined_mesh, new_stl_path):
  combined_mesh.save(new_stl_path)
  print(f"Gap adjusted. New STL file saved to: {new_stl_path}")


def translate_to_close_gap(mesh, offset):
  min_point = np.min(mesh.vectors[:, :, 2])
  max_point = np.max(mesh.vectors[:, :, 2])
  mid_point = (max_point + min_point) / 2
  for vector in mesh.vectors:
    if np.any(vector[:, 2] > mid_point):
      vector[:, 2] -= (max_point - mid_point) - offset
  return mesh


# Integrated main function
def main():
  image_path = "/Users/titeershaghatakchowdhury/Desktop/tryanderror/uploads/titeersha_1.jpg"
  bald_image_path = "/Users/titeershaghatakchowdhury/Desktop/tryanderror/uploads/bald head.jpg"
  output_folder = "/Users/titeershaghatakchowdhury/Desktop/tryanderror/output"
  os.makedirs(output_folder, exist_ok=True)

  load_image_and_create_stl(image_path,
                            output_folder,
                            'face_mesh',
                            height_factor=0.3)
  load_image_and_create_stl(bald_image_path,
                            output_folder,
                            'bald_head_mesh',
                            height_factor=0.3)

  face_stl_path = os.path.join(output_folder, 'face_mesh.stl')
  bald_head_stl_path = os.path.join(output_folder, 'bald_head_mesh.stl')
  combined_stl_path = os.path.join(output_folder, 'combined_mesh.stl')

  merge_stl(face_stl_path, bald_head_stl_path, combined_stl_path)

  stl_path_no_edge = os.path.join(output_folder, 'combined_mesh_no_edges.stl')
  remove_non_face_edges_from_stl(combined_stl_path, stl_path_no_edge)

  final_stl_path = os.path.join(output_folder, 'final_mesh.stl')
  original_mesh = load_mesh(stl_path_no_edge)
  adjusted_mesh = translate_to_close_gap(original_mesh, offset=0.8)

  save_mesh(adjusted_mesh, final_stl_path)


if __name__ == "__main__":
  main()
