from streetview import get_panorama_meta, search_panoramas, get_streetview, get_panorama
import os, time, csv
from PIL import Image, PngImagePlugin
import threading
import requests
from itertools import islice
from requests.exceptions import Timeout, ConnectionError

# API key
# key = os.environ["API_KEY"]
key = "API_KEY_PLACEHOLDER"
########## Progress bar functions ############################

def display_progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    # Move the cursor up one line and then print the progress bar
    print(f"""\rProgress: [{arrow + spaces}] {int(progress * 100)}%
""", end='')


def spinning_wheel(duration=0.1):
    wheel_sequence = ['|', '/', '-', '\\']
    wheel_index = 0
    while keep_spinning:
        wheel_char = wheel_sequence[wheel_index % len(wheel_sequence)]
        print(f"\r{wheel_char} ", end='', flush=True)
        time.sleep(duration)
        wheel_index += 1


############## Data functions ###################################

def slice_from_key(data, key) -> dict():
    """
    
    Slices a dictionary from given key (param)
    
    """
    return dict(islice(data.items(), list(data.keys()).index(key), None))

def get_address_from_coordinates(coordinates):
    """
    
    # Example usage:
    coordinates = (52.506810, 13.491683)
    address = get_address_from_coordinates(coordinates)
    print(address["display_name"])
    
    """
    BASE_URL = "https://nominatim.openstreetmap.org/reverse"    
    params = {
        "lat": coordinates[0],
        "lon": coordinates[1],
        "format": "json"
    }
    
    headers = {
        "User-Agent": "YourAppName/1.0"  # Replace 'YourAppName' with the name of your app
    }    
    response = requests.get(BASE_URL, params=params, headers=headers)
    data = response.json()
    if data:
        data = slice_from_key(data, 'lat')
        data.pop('boundingbox', None)
        data.pop('importance', None)
        data.pop('place_rank', None)
        return data
    else:
        return None

def get_coordinates_from_address(address) -> tuple():
    """
    
    # Example usage:
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    coords = get_coordinates_from_address(address)
    print(coords)
    
    """
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    
    headers = {
        "User-Agent": "YourAppName/1.0"  # Replace 'YourAppName' with the name of your app
    }
    
    response = requests.get(BASE_URL, params=params, headers=headers)
    data = response.json()
    
    if data:
        return (float(data[0]['lat']), float(data[0]['lon']))
    else:
        return None

def get_cropped_street_view_img(meta_list):
    # Get "normal" imgs (no pano) for every MetaData object and save them as png
    # Use a relative path for the directory
    directory_streetview = "imgs/streetviews"
    
    # Check and create the directory if it doesn't exist
    if not os.path.exists(directory_streetview):
        os.makedirs(directory_streetview)
    
    # Control variable for the spinning wheel
    keep_spinning = True
    # Start the spinning wheel in a separate thread
    wheel_thread = threading.Thread(target=spinning_wheel)
    wheel_thread.start()
    
    for index, x in enumerate(meta_list):
        # Fetch additional metadata from panos_dict
        pano_data = panos_dict.get(x.pano_id, None)
        if not pano_data:
            continue  # Skip if no matching data in panos
            
        # Fetch the address using the coordinates
        coordinates = (x.location.lat, x.location.lng)
        address = get_address_from_coordinates(coordinates)
        address_display_name = address["display_name"]
        address_zip_code = address["address"]['postcode']
            
        # Create a subfolder named after Zip code within the date folder
        zip_code_directory = os.path.join(directory_streetview, address_zip_code)
        if not os.path.exists(zip_code_directory):
            os.makedirs(zip_code_directory)

        # Create a subfolder named after address_display_name within the date folder
        address_directory = os.path.join(zip_code_directory, address_display_name)
        if not os.path.exists(address_directory):
            os.makedirs(address_directory)
            
        image = get_streetview(
            pano_id=x.pano_id,
            api_key=key,
        )    
        
        # Convert the image to a PIL Image object
        pil_image = image
    
        # Create metadata for the image
        meta_info = PngImagePlugin.PngInfo()
        meta_info.add_text("date", x.date)
        meta_info.add_text("lat", str(x.location.lat))
        meta_info.add_text("lng", str(x.location.lng))
        meta_info.add_text("pano_id", x.pano_id)
        meta_info.add_text("address", address_display_name)
        meta_info.add_text("heading", str(pano_data.heading))
        meta_info.add_text("pitch", str(pano_data.pitch))
        meta_info.add_text("roll", str(pano_data.roll))
    
        
        # Save the image with metadata as PNG in the address subfolder
        pil_image.save(f"{address_directory}/{x.date}-{x.pano_id}.png", "PNG", pnginfo=meta_info)
    
        # Write merged metadata to a CSV file
        csv_filename = os.path.join(address_directory, "metadata.csv")
        with open(csv_filename, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # If the file is empty, write the headers
            if csv_file.tell() == 0:
                csv_writer.writerow(["pano_id", "date", "lat", "lng", "heading", "pitch", "roll"])
            csv_writer.writerow([x.pano_id, x.date, x.location.lat, x.location.lng, pano_data.heading, pano_data.pitch, pano_data.roll])
        
        # Update the progress bar
        display_progress_bar(index + 1, total_images)
        
    # Stop the spinning wheel
    keep_spinning = False
    wheel_thread.join()  # Wait for the wheel thread to finish
    
    print("\nDone!")

def get_panorama_street_view_img(meta_list):
    directory_panos = "imgs/panoramas"
    # Check and create the directory if it doesn't exist
    if not os.path.exists(directory_panos):
        os.makedirs(directory_panos)
        
    total_images = len(meta_list)
    
    # Control variable 
    keep_spinning = True
    
    # Start the spinning wheel in a separate thread
    wheel_thread = threading.Thread(target=spinning_wheel) 
    wheel_thread.start()
    
    for index, x in enumerate(meta_list):
        try:
            # Fetch additional metadata from panos_dict
            pano_data = panos_dict.get(x.pano_id, None)
            if not pano_data:
                continue  # Skip if no matching data in panos
        
            # Fetch the address using the coordinates
            coordinates = (x.location.lat, x.location.lng)
            address = get_address_from_coordinates(coordinates)
            address_display_name = address["display_name"]
            address_zip_code = address["address"]['postcode']
            
            # Create a subfolder named after Zip code within the date folder
            zip_code_directory = os.path.join(directory_panos, address_zip_code)
            if not os.path.exists(zip_code_directory):
                os.makedirs(zip_code_directory)
    
            # Create a subfolder named after address_display_name within the date folder
            address_directory = os.path.join(zip_code_directory, address_display_name)
            if not os.path.exists(address_directory):
                os.makedirs(address_directory)         
                
            max_retries = 3
            retries = 0    
            while retries < max_retries:
                try:
                    image = get_panorama(pano_id=x.pano_id)
                    # Convert the image to a PIL Image object
                    pil_image = image
                
                    # Create metadata for the image
                    meta_info = PngImagePlugin.PngInfo()
                    meta_info.add_text("date", x.date)
                    meta_info.add_text("lat", str(x.location.lat))
                    meta_info.add_text("lng", str(x.location.lng))
                    meta_info.add_text("pano_id", x.pano_id)
                    meta_info.add_text("address", address_display_name)
                    meta_info.add_text("heading", str(pano_data.heading))
                    meta_info.add_text("pitch", str(pano_data.pitch))
                    meta_info.add_text("roll", str(pano_data.roll))
                    
                     # Save the image with metadata as PNG in the date subfolder
                    pil_image.save(f"{address_directory}/{x.date}-{x.pano_id}.png", "PNG", pnginfo=meta_info)
                    
                    # Write merged metadata to a CSV file
                    csv_filename = os.path.join(address_directory, "metadata.csv")
                    
                    with open(csv_filename, mode='a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        # If the file is empty, write the headers
                        if csv_file.tell() == 0:
                            csv_writer.writerow(["pano_id", "date", "lat", "lng", "heading", "pitch", "roll", "address"])
                        csv_writer.writerow([x.pano_id, x.date, x.location.lat, x.location.lng, 
                                             pano_data.heading, pano_data.pitch, pano_data.roll, 
                                             address_display_name])
                        break
                except Timeout:
                    print("The request timed out! Retrying...")
                    retries += 1
                except ConnectionError:
                    print("There was a connection error! Retrying...")
                    retries += 1
                except Exception as e:         
                    print(f"Unexpected error for pano_id {x.pano_id}. Error: {e}")
                    break
        except Exception as e:
            print(x.pano_id, "Skipped.\nTraceback:", e, "\n")
        
        # Update the progress bar
        display_progress_bar(index + 1, total_images)
        

        
    print("\nDone!")

"""

Find more coordinates by address with the get_coordinates_from_address()
function defined above. 

Example Coords:
Berghain (52.510594, 13.442860)
Kotti (52.4989853, 13.4183107)
Gisela (52.506756, 13.491681)
"""
find_coords = True
while find_coords:
    inp_choice_location = input("Input an address (include Zip code):")
    coords = get_coordinates_from_address(inp_choice_location)
    if coords is None:
        print(f"{inp_choice_location} is seemingly too vague or not included in the db.")
    else:
        # Create list of panorama objects based on coordinates
        panos = search_panoramas(coords[0],coords[1])
        print(panos[0])
        break

# Create a dictionary from panos for easy lookup
panos_dict = {pano.pano_id: pano for pano in panos}

# Get metadata of nearest available panoramas
meta_list = []
print("Trying to fetch metadata for the images...")
# Control variable 
keep_spinning = True

# Start the spinning wheel in a separate thread
wheel_thread = threading.Thread(target=spinning_wheel) 
wheel_thread.start()
try:
    for x in panos:
        meta = get_panorama_meta(pano_id=x.pano_id, api_key=key)
        meta_list.append(meta)
except Exception as e:
    print("Traceback",e)
finally:
    print("Done.")
    # Stop the spinning wheel
    keep_spinning = False
    wheel_thread.join()  # Wait for the thread to finish
    
total_images = len(meta_list) # for the progress bar 
inp_choice_img_type = input(f"""Choose:
                                1. For cropped imgs.
                                2. For panorama imgs.
                                3. For both.
                             """)
if "1" in inp_choice_img_type:
    wheel_thread = threading.Thread(target=spinning_wheel) 
    wheel_thread.start()

    get_cropped_street_view_img(meta_list)

    keep_spinning = False
    wheel_thread.join()  # Wait for the thread to finish

elif "2" in inp_choice_img_type:
    wheel_thread = threading.Thread(target=spinning_wheel) 
    wheel_thread.start()
    
    get_panorama_street_view_img(meta_list)
    
    keep_spinning = False
    wheel_thread.join()  # Wait for the thread to finish

elif "3" in inp_choice_img_type:    
    wheel_thread = threading.Thread(target=spinning_wheel) 
    wheel_thread.start()

    get_cropped_street_view_img(meta_list)
    get_panorama_street_view_img(meta_list)

    keep_spinning = False
    wheel_thread.join()  # Wait for the thread to finish
else:
    print("invalid input. Closing app.")
    time.sleep(10)