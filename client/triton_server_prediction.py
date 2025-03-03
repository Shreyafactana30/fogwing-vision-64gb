"""Prediction from the Triton server."""
from typing import Any
import cv2
import numpy as np
import tritonclient.http as httpclient

_API_URL = 'localhost:8000'
_OUTPUT_KEYS = (
    'detection_classes',
    'detection_masks',
    'detection_boxes',
    'image_info',
    'num_detections',
    'detection_scores',
)

# Setting up the Triton client
triton_client = httpclient.InferenceServerClient(
    url=_API_URL, network_timeout=1200, connection_timeout=1200
)

# Outputs setup based on constants
outputs = [
    httpclient.InferRequestedOutput(key, binary_data=True)
    for key in _OUTPUT_KEYS
]


def model_input(path: str, height: int, width: int):
  """Prepares an image for input to a Triton model server.

  It reads it from a path, resizes it, normalizes it, and converts it to the
  format required by the server.

  Args:
      path: The file path to the image that needs to be processed.
      height: The height of the image to be resized.
      width: The width of the image to be resized.

  Returns:
      A Triton inference server input object containing the processed image.
  """
  image = cv2.imread(path)
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  image_resized = cv2.resize(
      image, (width, height), interpolation=cv2.INTER_AREA
  )
  transformed_img = np.expand_dims(image_resized, axis=0)
  inputs = httpclient.InferInput(
      'inputs', transformed_img.shape, datatype='UINT8'
  )
  inputs.set_data_from_numpy(transformed_img, binary_data=True)
  return inputs, image, image_resized


def _query_model(
    client: httpclient.InferenceServerClient,
    model_name: str,
    inputs: httpclient.InferInput,
):
  """Sends an inference request to the Triton server.

  Args:
      client: The Triton server client.
      model_name: Name of the model for which inference is requested.
      inputs: The input data for inference.

  Returns:
      The result of the inference request.
  """
  return client.infer(model_name=model_name, inputs=[inputs], outputs=outputs)


def prediction(
    model_name: str, inputs: httpclient.InferInput
):
  """Model name for prediction.

  Args:
      model_names: Model name in Triton
        Server.
      inputs: The input data for inference.

  Returns:
      prediction output from the model.
  """
  result = _query_model(triton_client, model_name, inputs)
  print(result)
  result_dict = {key: result.as_numpy(key) for key in _OUTPUT_KEYS}
  return result_dict
