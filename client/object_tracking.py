"""Object tracking functions."""

import trackpy as tp

# Define the replacement criteria
_REPLACEMENT_CRITERIA = {'Plastics_PET_Na': 'Plastics_PET_Bottle'}


def apply_tracking(df,
        search_range_x, 
        search_range_y,
        memory=20):
  """Apply tracking to the dataframe.

  Args:
    df: The dataframe to apply tracking to.
    search_range_x: The search range of pixels for tracking along x axis.
    search_range_y: The search range of pixels for tracking along y axis.
    memory: The frames memory for tracking.

  Returns:
    The tracking result dataframe.
  """
  # Define the columns to link for tracking
  tracking_columns = [
      'x',
      'y',
      'frame',
      # 'area',
      # 'label',
      # 'color'
      # 'bbox_0',
      # 'bbox_1',
      # 'bbox_2',
      # 'bbox_3',
      'major_axis_length',
      'minor_axis_length',
      'eccentricity',
      # # 'convex_area',
      # 'mean_intensity-0',
      # 'mean_intensity-1',
      # 'mean_intensity-2',
      # 'max_intensity-0',
      # 'max_intensity-1',
      # 'max_intensity-2',
      # 'min_intensity-0',
      # 'min_intensity-1',
      # 'min_intensity-2',
      # 'perimeter',
  ]

  # Perform the tracking operation on the specified columns
  track_df = tp.link_df(df[tracking_columns], search_range=(search_range_y, search_range_x), memory=memory)

  # Copy the additional columns from the original dataframe
  additional_columns = [
      'source_name',
      'image_name',
      'detection_scores',
      'detection_classes_names',
      'detection_classes',
      'color',
      'creation_time'
  ]
  track_df[additional_columns] = df[additional_columns]

  track_df.drop(columns=['frame'], inplace=True)
  track_df.reset_index(drop=True, inplace=True)

  return track_df


def process_tracking_result(df):
  """Process the tracking result dataframe.

  Args:
    df: The tracking result dataframe.

  Returns:
    The processed tracking result dataframe.
  """
  # Group by 'particle' and get the max value from 'detection_scores'
  grouped = (
      df.groupby('particle')
      .agg({
          'source_name': 'first',
          'image_name': 'first',
          'detection_scores': 'max',
          'detection_classes': 'first',
          'detection_classes_names': 'first',
          'color': 'first',
          'creation_time': 'first'
      })
      .reset_index()
  )
  return grouped
