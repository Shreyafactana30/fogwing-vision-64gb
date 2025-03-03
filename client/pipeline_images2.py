"""Pipeline to run the prediction on the images with Triton server."""

import datetime
import time
import logging
import os
import sys
from absl import app
from absl import flags

sys.path.append(
    "models/official/projects/waste_identification_ml/model_inference/"
)
import color_and_property_extractor
import cv2
import feature_extraction
import mask_bbox_saver
import numpy as np
import object_tracking
import pandas as pd
import triton_server_prediction
import utils
import json
from generic_colors import G_COLORS
from PIL import Image
import requests
from collections import defaultdict #new import

sent_ptime = 0

sys.path.append("models/research/")
from object_detection.utils import visualization_utils as viz_utils

import labels

INPUT_DIRECTORY = flags.DEFINE_string(
    "input_directory", None, "The path to the directory containing images."
)

PREDICTED_IMAGES = flags.DEFINE_string(
    "predicted_images", None, "The path to the directory to save the results."
)

IMAGE_TO_UI = flags.DEFINE_string(
    "image_to_ui", None, "The path to the directory to display the predicted results."
)

HEIGHT = flags.DEFINE_integer(
    "height", None, "Height of an image required by the model"
)

WIDTH = flags.DEFINE_integer(
    "width", None, "Width of an image required by the model"
)

MODEL = flags.DEFINE_string("model", None, "Model name")


PREDICTION_THRESHOLD = flags.DEFINE_float(
    "score", 0.40, "Threshold to filter the prediction results"
)


SEARCH_RANGE_X = flags.DEFINE_integer(
    "search_range_x", None, "Pixels upto which every object needs to be tracked along X axis."
)

SEARCH_RANGE_Y = flags.DEFINE_integer(
    "search_range_y", None, "Pixels upto which every object needs to be tracked along Y axis."
)

MEMORY = flags.DEFINE_integer(
    "memory", None, "Frames upto which every object needs to be tracked."
)

PAYLOADS = flags.DEFINE_string(
    "payloads", None, "Prediction of each image is stored in payloads."
)

CONFIG_PATH = flags.DEFINE_string(
    "config_path", None, "Prediction of each image is stored in payloads."
)

#category_indices, category_index = labels.load_labels(_LABELS)
#id_to_name_map = {obj["name"]: obj["id"] for obj in category_index.values()}


def is_image_broken(image_path: str) -> bool:
    """Check if an image file is broken.



    Args:
        file_path (str): The path to the image file.



    Returns:
        bool: True if the image is broken, False otherwise.
    """

    try:
        img = Image.open(image_path)  # open the image file
        img.verify()  # verify that it is, in fact an image
        return False  # Image is not broken
    except (IOError, SyntaxError) as e:
        return True  # Image is broken




def main(_) -> None:
    # Read the labels for the model.
    labels_path = os.path.join(os.getcwd(), "labels.csv")
    labels_names, category_index = utils.load_labels(labels_path)

    # Create the output directory if it does not exist.
    os.makedirs(PREDICTED_IMAGES.value, exist_ok=True)

    # Create the logs directory if it does not exist.
    log_name = os.path.basename(INPUT_DIRECTORY.value) + '_' + datetime.datetime.now().strftime("%Y-%m-%d")

    _LOGS_FOLDER = os.path.join(os.getcwd(), "logs")
    os.makedirs(_LOGS_FOLDER, exist_ok=True)
    logger = utils.create_log_file(log_name, _LOGS_FOLDER)

    batch_number = 1
    while True:
        features_set = []
        image_names_list = []
        

        # Read files from a folder.
        files = utils.files_paths(INPUT_DIRECTORY.value) #customized files_paths

        if len(files)>1:
          
          for frame, image_path in enumerate(files[:10], start=1):
            # Group file names by their order IDs
            
          
          
            # Send the image to triton server and get the prediction.

            if os.path.getsize(image_path) == 0:
                logger.info("image contains 0 bytes")
                os.remove(image_path)


            elif is_image_broken(image_path):
                os.remove(image_path)

            else:
                logger.info(f"\nProcessing {os.path.basename(image_path)}")
                original_img_basename = os.path.basename(image_path)

                image_names_list.append(original_img_basename)
                
                print("image_names_list",image_names_list)
                



                try:
                    inputs, original_image, resized_image = (
                        triton_server_prediction.model_input(
                            image_path, HEIGHT.value, WIDTH.value
                        )
                    )
                    logger.info(
                        f"Successfully read an image for {os.path.basename(image_path)}"
                    )

                    original_height, original_width, resized_height, resized_width = (
                        original_image.shape[0],
                        original_image.shape[1],
                        resized_image.shape[0],
                        resized_image.shape[1],
                    )

                    creation_time = os.path.getctime(image_path)
                except Exception as e:
                    logger.info(f"Failed to read an image.")
                    logger.info(e)
                    continue

                try:
                    #model_names = [MATERIAL_MODEL.value, MATERIAL_FORM_MODEL.value]
                    model_name = MODEL.value
                    print("model_name",model_name)
                    start = time.time()
                    result = triton_server_prediction.prediction(model_name, inputs)
                    #print("result",result)
                    end = time.time()
                    logger.info(
                        f"Total predictions:{result['num_detections'][0]}"
                    )

                    logger.info(
                        f"Successfully got prediction for {os.path.basename(image_path)}"
                    )
                    
                except Exception as e:
                    logger.info(
                        f"Failed to get prediction for {os.path.basename(image_path)}"
                    )
                    logger.info(e)
                    continue

                try:
                    # Set the object area threshold to filter the prediction results.
                    area_threshold = 0.3 * np.product(resized_image.shape[:3])

                    
                    if result["num_detections"][0]:
                        scores = result["detection_scores"][0]
                        filtered_indices = scores > PREDICTION_THRESHOLD.value

                        if any(filtered_indices):
                            # Filter the prediction results based on the score threshold.
                            result = utils.filter_detection(result, filtered_indices)
                    else:
                        logger.info("Zero predictions afte threshold.")
                        continue

                    if result["num_detections"][0]:
                        # Normalize the bounding boxes according to the resized image size.
                        result["normalized_boxes"] = result["detection_boxes"].copy()
                        result["normalized_boxes"][:, :, [0, 2]] /= resized_height
                        result["normalized_boxes"][:, :, [1, 3]] /= resized_width
 
                        # Reframe the masks to the resized image size.
                        result["detection_masks_resized"] = utils.reframe_masks(
                            result, "normalized_boxes", resized_height, resized_width
                        )
 
                        # Filter the prediction results based on the area threshold and
                        # remove the overlapping masks.
                        unique_indices = utils.filter_masks(
                            result["detection_masks_resized"],
                            iou_threshold=0.80,
                            area_threshold=area_threshold,
                        )
                        result = utils.filter_detection(result, unique_indices)
                        result['detection_classes_names'] = np.array([[str(labels_names[i-1]) for i in result['detection_classes'][0]]])
                        logger.info(f"Total predictions after processing: {result['num_detections'][0]}")
                        print("result['detection_classes_names']",result['detection_classes_names'])
                   
                    else:
                        logger.info("Zero predictions after postprocessing.")
                        os.remove(image_path)
                        continue
                except Exception as e:
                      logger.info("Failed to process prediction results.")
                      os.remove(image_path)
                      logger.info(e)
                      continue

                try:
                        # Adjust the image size to ensure both dimensions are at least 1024
                        # for saving images with bbx and masks.
                        height_plot, width_plot = utils.adjust_image_size(
                            original_height, original_width, 1024
                        )
                        image_plot = cv2.resize(
                            original_image,
                            (width_plot, height_plot),
                            interpolation=cv2.INTER_AREA,
                        )
                        result["detection_masks_reframed"] = utils.resize_each_mask(
                            result["detection_masks_resized"],
                            height_plot,
                            width_plot,
                        )

                        _, image_new = mask_bbox_saver.save_bbox_masks_labels(
                            result,
                            image_plot,
                            os.path.basename(image_path),
                            IMAGE_TO_UI.value,
                            category_index,
                            PREDICTION_THRESHOLD.value,
                            
                        )

                        # image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        image_new = cv2.cvtColor(image_new, cv2.COLOR_BGR2RGB)

                        cv2.imwrite(IMAGE_TO_UI.value, image_new)
                        
                        order_ids = [os.path.splitext(img)[0].split("_")[1] for img in image_names_list] #new
                        
                        global sent_ptime
                        
                         
                        config_path = CONFIG_PATH.value

                        with open(config_path, "r") as config_path:
                            time_interval = json.loads(config_path.read()).get("UPLOAD_INTERVAL")

                        current_ptime = time.time()
                        if (current_ptime - sent_ptime) >= time_interval and len(set(order_ids)) == 1 :
                            file_name, image_new = mask_bbox_saver.save_bbox_masks_labels(
                                result,
                                image_plot,
                                os.path.basename(image_path),
                                PREDICTED_IMAGES.value,
                                category_index,
                                PREDICTION_THRESHOLD.value,
                            )
  
                            # image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            image_new = cv2.cvtColor(image_new, cv2.COLOR_BGR2RGB)

                            cv2.imwrite(os.path.join(PREDICTED_IMAGES.value, file_name), image_new)
                            sent_ptime = time.time()
                            b=current_ptime - sent_ptime
                            print("current_ptime - sent_ptime",b)

                              # in save_bbox_masks_labels return filename i.e os.path.basename(image_path) and  it will look like
                              # filename=mask_bbox_saver.save_bbox_masks_labels and call this in payload_data function by passing as parameter
                              # note: before writing only you save cv2.imwrite
                              # then match if oiginal image name == filename then save filename in json
                            
                        os.remove(image_path)

                        logger.info(f"Successfully saved bbox and masks.")
                except Exception as e:
                    logger.info(
                        f"Failed to save bbox masks labels."
                    )
                    logger.info(e)
                    continue

                try:
                    height_tracking, width_tracking = utils.adjust_image_size(
                        resized_height, resized_width, 300
                    )
                    
                    tracking_image = cv2.resize(
                    np.squeeze(resized_image),
                    (width_tracking, height_tracking),
                    interpolation=cv2.INTER_AREA
                    )
                    
                    
                    result["detection_masks_tracking"] = utils.resize_each_mask(
                        result["detection_masks_resized"],
                        height_tracking,
                        width_tracking,
                    )
                    
                   
                    # Extract the properties of the mask using computer vision techniques.
                    features = feature_extraction.extract_properties(
                        tracking_image, result, "detection_masks_tracking"
                    )
                    

                    
                    features["source_name"] = os.path.basename(INPUT_DIRECTORY.value)
                    features["image_name"] = os.path.basename(image_path)
                    features["creation_time"] = creation_time
                    features["frame"] = frame
                    features["detection_scores"] = result["detection_scores"][0]
                    features["detection_classes"] = result["detection_classes"][0]
                    features["detection_classes_names"] = result["detection_classes_names"][0]
                    
                    

                    logger.info(f"Successfully extracted properties.")
                except Exception as e:
                    logger.info(
                        f"Failed to extract properties."
                    )
                    logger.info(e)
                    continue

                try:
                    
                    
                    result['detection_boxes'] = result["detection_boxes"].round().astype(int)

                    # Extract the objects masks from the prediction results in order to
                    # calculate the dominant colors.
                    cropped_objects = utils.extract_and_resize_objects(
                        result,
                        "detection_masks_resized",
                        "detection_boxes",
                        np.squeeze(resized_image),
                    )


                    # Use clustering technique to find the dominant colors of the objects.
                    dominant_colors = [
                        *map(
                            color_and_property_extractor.find_dominant_color, cropped_objects
                        )
                    ]

                    specific_color_names = [
                        *map(color_and_property_extractor.get_color_name, dominant_colors)
                    ]


                    generic_color_names = color_and_property_extractor.get_generic_color_name(dominant_colors,
                                                                                              generic_colors=G_COLORS)
                    # print("generic_color_names", generic_color_names)
                    # features['color'] = generic_color_names if generic_color_names else specific_color_names
                    features['color'] = generic_color_names if generic_color_names else specific_color_names
                    

                    features_set.append(features)
                    logger.info(f"Successfully done color detection.")
                    

                except Exception as e:
                    logger.info(f"Failed to extract color.")
                    logger.info(e)
                    continue

        try:
            if features_set:
                features_df = pd.concat(features_set, ignore_index=True)
                
                
                tracking_features = object_tracking.apply_tracking(
                    features_df,
                    search_range_x=SEARCH_RANGE_X.value,
                    search_range_y=SEARCH_RANGE_Y.value,
                    memory=MEMORY.value
                )
                # print("tracking_features",tracking_features)

                agg_features = object_tracking.process_tracking_result(tracking_features)
                counts = agg_features.groupby('detection_classes_names')['particle'].count()
                print(counts)


                #classes_colors = agg_features["detection_classes_names"] + "_" + agg_features["color"]
                classes_colors = agg_features.groupby(agg_features["detection_classes_names"].str.strip()+"_"+agg_features["color"])['particle'].count()
                material_count=agg_features.groupby(agg_features["detection_classes_names"])['particle'].count()
                print("material_count",material_count)
                print("type of material_count",type(material_count))
                
                print("classes_colors",classes_colors)
                
                
                tracking_results_dict = classes_colors.to_dict()
                print(tracking_results_dict)
                print(type(tracking_results_dict))

                '''
                # Count occurrences of each combined class and color
                combined_counts = classes_colors.value_counts()

                tracking_results_dict = {}

                # Print the combined counts in the desired format
                for combined, count in combined_counts.items():
                    # print(f"{combined}:{count}")

                    # print("object_tracking_sub_count",object_tracking_sub_count)
                    tracking_results_dict[combined] = count

                print("Tracking Results Dictionary:", tracking_results_dict)
                
                
                for i, count in tracking_results_dict.items():
                    for category in category_counts:
                        if category in i:
                            category_counts[category] += count

                print("category_counts",category_counts)
                
                '''


                payload_data(image_names_list, file_name, PAYLOADS, tracking_results_dict, batch_number)

                batch_number += 1  # Increment for the next batch
        except Exception as e:
            logger.info(f"Issue in object tracking.")
            logger.info(e)



#this is production payload function
success_counter = 0
def payload_data(image_names_list, file_name, PAYLOADS, object_tracking_sub_count, batch_number):
    """
    Saves batch details, category, subcategories data, and metadata to a JSON file,
    updating existing data to include new batch information.

    Args:
        image_names_list: contains image names in a list to process batchwise.
        file_name: name of the file to save
        PAYLOADS: path where the JSON file is being stored
        object_tracking_sub_count: Dictionary containing counts of tracked objects
        batch_number: It contains a batch number given for each batch of images to be processed.

    Returns:
        None
    """
    print("image_names_list",image_names_list)
    print("file_name",file_name) 
    
    
    global success_counter
    
    
    # Dictionary to count items
    counter = defaultdict(int)
    
    # Loop to count items based on the split key
    for key in object_tracking_sub_count:
        item = key.split("_")[0]
        counter[item] += object_tracking_sub_count[key]
    
    # Convert defaultdict to regular dict
    #updated_category_counts = dict(counter)
    updated_category_counts = {f"{key}_sum": value for key, value in counter.items()}
    
    # Display the result
    print(updated_category_counts)



    local = datetime.datetime.now()
    json_data = {}

    
    json_data = updated_category_counts       
    
    for original_img_basename in image_names_list:
        print(f"Comparing: '{original_img_basename}' with '{file_name}'")
        if original_img_basename.strip() == file_name.strip():  # Remove extra spaces or newlines
            print(f"Match found: {file_name}")
            json_data['image'] = file_name
        else:
            print(f"No match for: {file_name}")

            
            
            
        
    order_code = os.path.splitext(original_img_basename)[0].split("_")[1]
    product_name = os.path.splitext(original_img_basename)[0].split("_")[2]
      
    


    if object_tracking_sub_count:  # checks if the json is empty
        # Append order_code and product_name to object_tracking_sub_count dictionary
        object_tracking_sub_count['order_code'] = order_code #new
        object_tracking_sub_count['product_name'] = product_name #new

        resp=requests.put("http://127.0.0.1:7077/fwvision/qcinspection/update_qc_order", json=object_tracking_sub_count)
        
        # Check the status code and increment the counter
        if resp.status_code in {200, 201}:
            success_counter += 1
    
        print(f"Successful requests count: {success_counter}")
        
        print("resp.json()",resp.json())
        print("resp.status_code",resp.status_code)
        
        # Remove order_code and product_name from subcategory_counts
        del object_tracking_sub_count['order_code'] #new
        del object_tracking_sub_count['product_name'] #new
        
        print("object_tracking_sub_count",object_tracking_sub_count)
        
        if resp.status_code not in {200, 201}:
            return
        
                    

    else:
        json_data['others'] = "unknown"

    predicted_images_path = PREDICTED_IMAGES.value
    payload_data = PAYLOADS.value
    
    print("payload_data",payload_data)

    
    #order_code = os.path.splitext(original_img_basename)[0].split("_")[1]
    local = datetime.datetime.now()
    fname = f'{order_code}_batch-{batch_number}.json'
    file_path = os.path.join(PAYLOADS.value, fname)
 
    # Load existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            json_data = json.load(file)
 
 
    #product_name = os.path.splitext(original_img_basename)[0].split("_")[2]
    timestamp = local.timestamp()
 
    # json_data=updated_category_counts
 
    json_data["order_code"] = order_code
    
    print("order_code",order_code)
    json_data["product_name"] = product_name
    json_data["timestamp"] = timestamp
    json_data["event_code"] = 333
    json_data['product'] = object_tracking_sub_count
    
    print("json_data",json_data)
    
    if json_data:
      # Save the updated data back to the JSON file
      with open(file_path, 'w') as file:
          json.dump(json_data, file, indent=2)
    
    if os.path.getsize(file_path) == 0:
        logger.info(f"\nPayload is empty {(file_path)}")
        print("file_path", file_path)





if __name__ == "__main__":
    app.run(main)
