import pathlib
from PIL import Image
import google.generativeai as genai
import streamlit as st
import os

# Function to gather user input based on cuisine type
def recipe_input(cuisine):
    main_ingredient = st.text_input(f"Main ingredient for {cuisine}:")
    dietary_preference = st.text_input(f"Dietary preferences (optional) for {cuisine}:")
    cooking_time = st.text_input(f"Preferred cooking time (in minutes) for {cuisine}:")
    return main_ingredient, dietary_preference, cooking_time

# Streamlit App Layout
st.title("AI-Powered Recipe Generator")

# Select cuisine type
cuisine = st.selectbox(
    "Select a Cuisine Type",
    ("Italian", "Indian", "Mexican", "Chinese", "French")
)

# Configure the API key directly in the script
API_KEY = 'AIzaSyDkICa6LXV50JdSChVkjj9JrU6edWzrEgc'
genai.configure(api_key=API_KEY)

# Generation configuration
generation_config = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1000,
    "response_mime_type": "text/plain",
}

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Model name
MODEL_NAME = "gemini-1.5-flash"

# Create the model
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Get user inputs
main_ingredient, dietary_preference, cooking_time = recipe_input(cuisine)

# File uploader for ingredient images
uploaded_files = st.file_uploader("Upload images of ingredients...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
image_paths = []
index = 1

if uploaded_files:
    for img in uploaded_files:
        try:
            image = Image.open(img)
            st.image(image, use_column_width=True)
            
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            temp_image_path = pathlib.Path(f"temp_image_{index}.jpg")
            image.save(temp_image_path, format="JPEG")
            image_paths.append(temp_image_path)
            index += 1
        except Exception as e:
            st.error(f"Error processing image: {e}")

# Function to send a message to the model
def send_message_to_model(message, image_paths):
    image_inputs = []
    
    for image_path in image_paths:
        image_input = {
            'mime_type': 'image/jpeg',
            'data': pathlib.Path(image_path).read_bytes()
        }
        image_inputs.append(image_input)
        os.remove(image_path)
    
    response = chat_session.send_message([message] + image_inputs)
    return response.text

# Streamlit app logic
def main():
    if st.button("Generate Recipe"):
        st.write("Generating Recipe...")
        prompt = f"Generate a {cuisine} recipe using {main_ingredient}. Consider {dietary_preference} dietary preference and a cooking time of {cooking_time} minutes."
        response = send_message_to_model(prompt, image_paths)
        st.write(response)

if __name__ == "__main__":
    main()
