"""Extract properties of the mask."""

import numpy as np
import pandas as pd
import skimage.measure

_PROPERTIES = (
    'area',
    'bbox',
    'convex_area',
    'bbox_area',
    'major_axis_length',
    'minor_axis_length',
    'eccentricity',
    'centroid',
    'label',
    'mean_intensity',
    'max_intensity',
    'min_intensity',
    'perimeter'
)

def extract_properties(image, results, masks):
  """Extract properties of the mask.

  Args:
    image: Corresponding image of the mask.
    results: The detection results from the model.
    masks: The masks to extract properties from.

  Returns:
    The extracted properties.
  """
  list_of_df = []
  for mask in results[masks]:
    mask = np.where(mask, 1, 0)
    df = pd.DataFrame(
        skimage.measure.regionprops_table(mask, intensity_image=image, properties=_PROPERTIES)
    )
    list_of_df.append(df)
  features = pd.concat(list_of_df, ignore_index=True)
  features.rename(
      columns={
          'centroid-0': 'y',
          'centroid-1': 'x',
          'bbox-0': 'bbox_0',
          'bbox-1': 'bbox_1',
          'bbox-2': 'bbox_2',
          'bbox-3': 'bbox_3',
      },
      inplace=True,
  )
  return features
