import os
import glob
import json
import base64

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set your OpenAI API key
client = OpenAI(api_key=api_key)

def get_all_images(folder_path):
    """
    Recursively get all image files from a folder and its subfolders.
    
    :param folder_path: The top-level folder where images are located.
    :return: A list of image file paths.
    """
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(
            glob.glob(os.path.join(folder_path, '**', ext), recursive=True)
        )
    return image_files


def encode_image(image_path):
    """
    Read an image file and return its Base64-encoded string.
    
    :param image_path: Path to the image file.
    :return: Base64-encoded string of the image content.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def send_image_to_chatgpt(image_path, prompt):
    """
    Send a Base64-encoded image to ChatGPT with a given prompt.
    
    :param image_path: Path to the image file.
    :param prompt: The prompt to be used (currently unused in the request body).
    :return: The response object from the ChatGPT API.
    """
    base64_image = encode_image(image_path)

    with open(image_path, "rb"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the content of this image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

    return response


def process_images(folder_path, prompt, output_json_path):
    """
    Process all images in a folder, send them to ChatGPT, and append responses
    to a JSON file.

    :param folder_path: The folder path containing the images.
    :param prompt: The text prompt to use with ChatGPT (currently passed to the function,
                   but not included in the API call body).
    :param output_json_path: The path to the JSON file where results will be stored.
    """
    # Load existing data if file exists
    if os.path.exists(output_json_path):
        with open(output_json_path, 'r', encoding='utf-8') as f:
            try:
                responses = json.load(f)
            except json.JSONDecodeError:
                responses = []  # If file is empty or invalid
    else:
        responses = []

    images = get_all_images(folder_path)

    for image_path in images:
        print(f"Processing image: {image_path}")
        try:
            response = send_image_to_chatgpt(image_path, prompt)
            content = response.choices[0].message.content
            responses.append({
                "image_path": image_path,
                "response": content
            })
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    # Save updated responses back to the file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=4, ensure_ascii=False)

    print(f"Responses saved to {output_json_path}")


if __name__ == "__main__":
    folder_path = r"images"  # Replace with your folder path
    prompt = "Describe the content of this image."
    output_json_path = "responses.json"
    process_images(folder_path, prompt, output_json_path)
