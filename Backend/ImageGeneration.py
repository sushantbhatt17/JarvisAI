import asyncio
import os
import requests
import time
from random import randint
from PIL import Image
from dotenv import get_key

# Function to open and display generated images
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Ensure filenames are safe

    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            time.sleep(1)  # Pause before opening the next image

        except IOError:
            print(f"Unable to open {image_path}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = get_key(".env", "HuggingFaceAPIKey")
headers = {"Authorization": f"Bearer {API_KEY}"}

# Async function to send a request to Hugging Face API
async def query(payload):
    try:
        responses = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if responses.status_code == 200:
            return responses.data
        else:
            print(f"API Error: {responses.status_code}, {responses.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# Async function to generate images
async def generate_images(prompt: str):
    if not os.path.exists("Data"):
        os.makedirs("Data")  # Ensure the directory exists

    tasks = []

    # Create 4 image generation tasks
    for _ in range(3):
        payload = {"inputs": f"{prompt}, high quality, sharp, ultra HD, seed={randint(0, 1000000)}"}
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            filename = f"Data/{prompt.replace(' ', '_')}{i + 1}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {filename}")

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Run async image generation
    open_images(prompt)  # Open the generated images

# Main loop to monitor for image generation requests
while True:
    try:
        data_file = "Frontend/Files/ImageGeneration.data"

        # Ensure the file exists before reading
        if not os.path.exists(data_file):
            with open(data_file, "w") as f:
                f.write("False,False")

        # Read prompt and status
        with open(data_file, "r") as f:
            data = f.read().strip()

        Prompt, Status = data.split(",")

        # Check if image generation is requested
        if Status.strip().lower() == "true":
            print("Generating Images ...")
            GenerateImages(prompt=Prompt.strip())

            # Reset status after image generation
            with open(data_file, "w") as f:
                f.write("False,False")
            break  # Exit loop after processing

        else:
            time.sleep(1)  # Wait before checking again

    except:
        pass
