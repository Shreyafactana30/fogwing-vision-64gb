"""Utility functions for the pipeline."""

import csv
from typing import TypedDict
import logging
import os
import sys
import cv2
import natsort
import numpy as np
import tensorflow as tf

gpus = tf.config.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)


sys.path.append('models/research/')
from object_detection.utils import ops as utils_ops

class ItemDict(TypedDict):
  id: int
  name: str
  supercategory: str


def _read_csv_to_list(file_path: str):
  """Reads a CSV file and returns its contents as a list.

  This function reads the given CSV file, skips the header, and assumes
  there is only one column in the CSV. It returns the contents as a list of
  strings.

  Args:
      file_path: The path to the CSV file.

  Returns:
      The contents of the CSV file as a list of strings.
  """
  data_list = []
  with open(file_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      data_list.append(row[0])  # Assuming there is only one column in the CSV
  return data_list


def _categories_dictionary(objects):
  """This function takes a list of objects and returns a dictionaries.

  A dictionary of objects, where each object is represented by a dictionary
  with the following keys:
    - id: The ID of the object.
    - name: The name of the object.
    - supercategory: The supercategory of the object.

  Args:
    objects: A list of strings, where each string is the name of an
      object.

  Returns:
    A tuple of two dictionaries, as described above.
  """
  category_index = {}

  for num, obj_name in enumerate(objects, start=1):
    obj_dict = {'id': num, 'name': obj_name, 'supercategory': 'objects'}
    category_index[num] = obj_dict

  return category_index


def load_labels(labels_path: str):
    category_indices = _read_csv_to_list(labels_path)
    category_index = _categories_dictionary(category_indices)
    return category_indices, category_index


def filter_detection(results, valid_indices):
  """Filter the detection results based on the valid indices.

  Args:
    results: The detection results from the model.
    valid_indices: The indices of the valid detections.

  Returns:
    The filtered detection results.
  """
  if np.array(valid_indices).dtype == bool:
    new_num_detections = int(np.sum(valid_indices))
  else:
    new_num_detections = len(valid_indices)

  # Define the keys to filter
  keys_to_filter = [
      'detection_masks',
      'detection_masks_resized',
      'detection_masks_reframed',
      'detection_classes',
      'detection_boxes',
      'normalized_boxes',
      'detection_scores',
  ]

  filtered_output = {}

  for key in keys_to_filter:
    if key in results:
      if key == 'detection_masks':
        filtered_output[key] = results[key][:, valid_indices, :, :]
      elif key in ['detection_masks_resized', 'detection_masks_reframed']:
        filtered_output[key] = results[key][valid_indices, :, :]
      elif key in ['detection_boxes', 'normalized_boxes']:
        filtered_output[key] = results[key][:, valid_indices, :]
      elif key in ['detection_classes', 'detection_scores', 'detection_classes_names']:
        filtered_output[key] = results[key][:, valid_indices]
  filtered_output['image_info'] = results['image_info']
  filtered_output['num_detections'] = np.array([new_num_detections])

  return filtered_output


def _calculate_area(mask):
  """Calculate the area of the mask.

  Args:
    mask: The mask to calculate the area of.

  Returns:
    The area of the mask.
  """
  return np.sum(mask)


def _calculate_iou(mask1, mask2):
  """Calculate the intersection over union (IoU) between two masks.

  Args:
    mask1: The first mask.
    mask2: The second mask.

  Returns:
    The intersection over union (IoU) between the two masks.
  """
  intersection = np.logical_and(mask1, mask2).sum()
  union = np.logical_or(mask1, mask2).sum()
  return intersection / union if union != 0 else 0


def _is_contained(mask1, mask2):
  """Check if mask1 is entirely contained within mask2.

  Args:
    mask1: The first mask.
    mask2: The second mask.

  Returns:
    True if mask1 is entirely contained within mask2, False otherwise.
  """
  return np.array_equal(np.logical_and(mask1, mask2), mask1)


def filter_masks(masks, iou_threshold=0.8, area_threshold=None):
  """Filter the overlapping masks.

  Filter the masks based on the area and intersection over union (IoU).

  Args:
    masks: The masks to filter.
    iou_threshold: The threshold for the intersection over union (IoU) between
      two masks.
    area_threshold: The threshold for the area of the mask.

  Returns:
    The indices of the unique masks.
  """
  # Calculate the area for each mask
  areas = np.array([_calculate_area(mask) for mask in masks])

  # Sort the masks based on area in descending order
  sorted_indices = np.argsort(areas)[::-1]
  sorted_masks = masks[sorted_indices]
  sorted_areas = areas[sorted_indices]

  unique_indices = []

  for i, mask in enumerate(sorted_masks):
    if (area_threshold is not None and sorted_areas[i] > area_threshold) or sorted_areas[i] < 4000:
      continue

    keep = True
    for j in range(i):
      if _calculate_iou(mask, sorted_masks[j]) > iou_threshold or _is_contained(
          mask, sorted_masks[j]
      ):
        keep = False
        break
    if keep:
      unique_indices.append(sorted_indices[i])

  return unique_indices


def reframe_masks(results, boxes, height, width):
  """Reframe the masks to an image size.

  Args:
    results: The detection results from the model.
    boxes: The detection boxes.
    height: The height of the original image.
    width: The width of the original image.

  Returns:
    The reframed masks.
  """
  detection_masks = results['detection_masks'][0]
  detection_boxes = results[boxes][0]
  detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
      detection_masks, detection_boxes, height, width
  )
  detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, np.uint8)
  detection_masks_reframed = detection_masks_reframed.numpy()
  return detection_masks_reframed


def _combine_masks(mask1, mask2):
  """Combine two masks.

  Args:
    mask1: The first mask.
    mask2: The second mask.

  Returns:
    The combined mask.
  """
  return np.logical_or(mask1, mask2).astype(int)


def _combine_scores(score1, score2):
  """Calculate the average detection scores of two masks.

  Args:
    score1: The score of the first mask.
    score2: The score of the second mask.

  Returns:
    The combined score.
  """
  return (score1 + score2) / 2


def _combine_boxes(box1, box2):
  """Combine the bounding boxes of two masks.

  Args:
    box1: The first box.
    box2: The second box.

  Returns:
    The combined box.
  """
  ymin = min(box1[0], box2[0])
  xmin = min(box1[1], box2[1])
  ymax = max(box1[2], box2[2])
  xmax = max(box1[3], box2[3])
  return np.array([ymin, xmin, ymax, xmax])


def _combine_classes(class1, class2, category_indices):
  """Combine the classes of two masks.

  Args:
    class1: The class of the first mask.
    class2: The class of the second mask.
    category_indices: The mapping of category indices to category names.

  Returns:
    The combined class name.
  """
  class_name1 = category_indices[0][class1]
  class_name2 = category_indices[1][class2]
  return f'{class_name1}_{class_name2}'


def _find_class_id(combined_class_name, id_to_name_map):
  """Find the class id for the combined class name.

  Args:
    combined_class_name: The combined class name.
    id_to_name_map: The mapping of class names to class ids.

  Returns:
    The class id for the combined class name.
  """
  return id_to_name_map.get(combined_class_name, None)


def combine_similar_masks(
    result1, result2, category_indices, id_to_name_map, iou_threshold=0.8
):
  """Combine similar masks from two detection results.

  Args:
    result1: The first detection result.
    result2: The second detection result.
    category_indices: The mapping of category indices to category names.
    id_to_name_map: The mapping of category names to category ids.
    iou_threshold: The threshold for the intersection over union (IoU) between
      two masks.

  Returns:
    The combined detection result.
  """
  list1 = result1['detection_masks_resized']
  list2 = result2['detection_masks_resized']
  scores1 = result1['detection_scores'][0]
  scores2 = result2['detection_scores'][0]
  boxes1 = result1['normalized_boxes'][0]
  boxes2 = result2['normalized_boxes'][0]
  classes1 = result1['detection_classes'][0]
  classes2 = result2['detection_classes'][0]

  combined_masks = []
  combined_scores = []
  combined_boxes = []
  combined_classes = []
  combined_class_ids = []
  used_masks1 = np.zeros(len(list1), dtype=bool)
  used_masks2 = np.zeros(len(list2), dtype=bool)

  for i, (mask1, score1, box1, class1) in enumerate(
      zip(list1, scores1, boxes1, classes1)
  ):
    combined_mask = mask1
    combined_score = score1
    combined_box = box1
    combined_class_name = category_indices[0][class1]
    combined_with_any = False
    for j, (mask2, score2, box2, class2) in enumerate(
        zip(list2, scores2, boxes2, classes2)
    ):
      if used_masks2[j]:
        continue
      iou = _calculate_iou(mask1, mask2)
      contained1_in_2 = _is_contained(mask1, mask2)
      contained2_in_1 = _is_contained(mask2, mask1)

      if iou > iou_threshold or contained1_in_2 or contained2_in_1:
        combined_mask = _combine_masks(combined_mask, mask2)
        combined_score = _combine_scores(combined_score, score2)
        combined_box = _combine_boxes(combined_box, box2)
        combined_class_name = _combine_classes(class1, class2, category_indices)
        used_masks2[j] = True
        combined_with_any = True

    if combined_with_any:
      combined_class_id = _find_class_id(combined_class_name, id_to_name_map)
      combined_masks.append(combined_mask)
      combined_scores.append(combined_score)
      combined_boxes.append(combined_box)
      combined_classes.append(combined_class_name)
      combined_class_ids.append(combined_class_id)
      used_masks1[i] = True

  # Include masks from list1 that were not combined
  for i, (mask1, score1, box1, class1) in enumerate(
      zip(list1, scores1, boxes1, classes1)
  ):
    if not used_masks1[i]:
      combined_class_name = f'{category_indices[0][class1]}_Na'
      combined_class_id = _find_class_id(combined_class_name, id_to_name_map)
      combined_masks.append(mask1)
      combined_scores.append(score1)
      combined_boxes.append(box1)
      combined_classes.append(combined_class_name)
      combined_class_ids.append(combined_class_id)

  # Include masks from list2 that were not combined
  for j, (mask2, score2, box2, class2) in enumerate(
      zip(list2, scores2, boxes2, classes2)
  ):
    if not used_masks2[j]:
      combined_class_name = f'Na_{category_indices[1][class2]}'
      combined_class_id = _find_class_id(combined_class_name, id_to_name_map)
      combined_masks.append(mask2)
      combined_scores.append(score2)
      combined_boxes.append(box2)
      combined_classes.append(combined_class_name)
      combined_class_ids.append(combined_class_id)

  num_detections = len(combined_masks)

  combined_result = {
      'detection_masks_resized': np.array(combined_masks, dtype=np.uint8),
      'detection_scores': np.array([combined_scores], dtype=np.float32),
      'normalized_boxes': np.array([combined_boxes], dtype=np.float32),
      'detection_classes_names': np.array([combined_classes]),
      'detection_classes': np.array([combined_class_ids], dtype=np.int32),
      'num_detections': np.array([num_detections], dtype=np.int64),
  }

  return combined_result


def resize_each_mask(masks, target_height, target_width):
  """Resize each mask to the target height and width.

  Args:
    masks: The masks to resize.
    target_height: The target height of the resized masks.
    target_width: The target width of the resized masks.

  Returns:
    The resized masks.
  """
  combined_masks = []
  for i in masks:
    mask = cv2.resize(
        i, (target_width, target_height), interpolation=cv2.INTER_NEAREST
    )
    combined_masks.append(mask)
  return np.array(combined_masks)


def files_paths(folder_path):
  """List the full paths of image files in a folder and sort them.

  Args:
    folder_path: The path of the folder to list the image files from.

  Returns:
    A list of full paths of the image files in the folder, sorted in ascending
    order.
  """
  img_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
  image_files_full_path = []

  for entry in os.scandir(folder_path):
    if entry.is_file() and entry.name.lower().endswith(img_extensions):
      image_files_full_path.append(entry.path)

  # Sort the list of files by name
  image_files_full_path = natsort.natsorted(image_files_full_path)

  return image_files_full_path


def extract_and_resize_objects(results, masks, boxes, image, resize_factor=0.5):
  """Extract and resize objects from the detection results.

  Args:
    results: The detection results from the model.
    masks: The masks to extract objects from.
    boxes: The bounding boxes of the objects.
    image: The image to extract objects from.
    resize_factor: The factor by which to resize the objects.

  Returns:
    A list of cropped objects.
  """
  cropped_objects = []

  for i, mask in enumerate(results[masks]):
    ymin, xmin, ymax, xmax = results[boxes][0][i]
    mask = np.expand_dims(mask, axis=-1)

    # Crop the object using the mask and bounding box
    cropped_object = np.where(
        mask[ymin:ymax, xmin:xmax], image[ymin:ymax, xmin:xmax], 0
    )

    # Calculate new dimensions
    new_width = int(cropped_object.shape[1] * resize_factor)
    new_height = int(cropped_object.shape[0] * resize_factor)
    cropped_object = cv2.resize(
        cropped_object, (new_width, new_height), interpolation=cv2.INTER_AREA
    )
    cropped_objects.append(cropped_object)

  return cropped_objects


def adjust_image_size(height, width, min_size):
  """Adjust the image size to ensure both dimensions are at least 1024.

  Args:
    height: The height of the image.
    width: The width of the image.
    min_size: Minimum size of the image dimension needed. 

  Returns:
    The adjusted height and width of the image.
  """
  if height < min_size or width < min_size:
    return height, width

  # Calculate the scale factor to ensure both dimensions remain at least 1024
  scale_factor = min(height / min_size, width / min_size)

  new_height = int(height / scale_factor)
  new_width = int(width / scale_factor)

  return new_height, new_width


def create_log_file(name: str, logs_folder_path: str):
  """Creates a logger and a log file given the name of the video.

  Args:
    name: The name of the video.
    logs_folder_path: Path to the directory where logs should be saved.

  Returns:
    logging.Logger: Logger object configured to write logs to the file.
  """
  log_file_path = os.path.join(logs_folder_path, f'{name}.log')
  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  file_handler = logging.FileHandler(log_file_path)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  return logger
