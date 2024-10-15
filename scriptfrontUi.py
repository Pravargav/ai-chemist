
import pathlib
from PIL import Image
import google.generativeai as genai
import streamlit as st
import os

# Function for scenario-specific suggestions
def ai_chemist_simulation(scenario):
    if scenario == "Pharmaceutical Research":
      target = st.text_input(f"target_bacterial_enzymes {scenario}:")
      constraints=""
      stability=""
    elif scenario == "Green Chemistry":
      target = st.text_input(f"target_properties_of_pesticides {scenario}:")
      constraints = st.text_input(f"environmental_constraints {scenario}:")
      stability=""
    elif scenario == "Polymer Science":
      target = st.text_input(f"target_mechanical_properties {scenario}:")
      constraints=""
      stability = st.text_input(f"chemical_stability {scenario}:")
    return target,constraints,stability

# Streamlit App Layout
st.title("AI Chemist Assistance.")

# Select scenario
scenario = st.selectbox(
    "Select a Scenario",
    ("Pharmaceutical Research", "Green Chemistry", "Polymer Science")
)
# Configure the API key directly in the script
API_KEY = 'AIzaSyBn8GmBfRLcjtZHz-zqQrZqzbfWaJ9n06o'
genai.configure(api_key=API_KEY)

# Generation configuration
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
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
MODEL_NAME = "gemini-1.5-pro-latest"


# Create the model
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])
target,constraints,stability= ai_chemist_simulation(scenario) 
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"],  accept_multiple_files=True)
impaths=[]
idx=2
if uploaded_files is not None:
    for img in uploaded_files:
        try:
            # Load and display the image
            image = Image.open(img)
            st.image(image, use_column_width=True)

            # Convert image to RGB mode if it has an alpha channel
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Save the uploaded image temporarily
            idx+=2
            temp_image_path = pathlib.Path(f"temp_image_{idx}.jpg")
            image.save(temp_image_path, format="JPEG")
            impaths.append(temp_image_path)
            # Generate UI description
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
# Function to send a message to the model

def send_message_to_model(message, image_paths):
    image_inputs = []
    
    for image_path in image_paths:
      print(image_path)
      
      image_input = {
          'mime_type': 'image/jpeg',
          'data': pathlib.Path(image_path).read_bytes()
      }
      image_inputs.append(image_input)
      os.remove(image_path)
    # Combine the message and image inputs
    response = chat_session.send_message([message] + image_inputs)
    return response.text

# Streamlit app
def main():
    
     
    if st.button("Run AI Chemist Simulation"):
            if(scenario=="Pharmaceutical Research"):
                t="Generate a list of potential compounds and environmentally benign synthesis methods. monitor the reactions in real-time, ensuring that the processes minimize waste and energy consumption. provide insights into the biodegradability and toxicity of the products, helping  develop a sustainable pesticide that meets regulatory standards and is safe for the environment."
            elif(scenario=="Polymer Science"):
                t="Suggest various monomers and polymerization techniques. Give recommendations, synthesizing the polymers in her lab. the real-time monitoring capabilities should allow us to adjust reaction parameters to optimize polymer properties. Provide immediate feedback on the tensile strength and thermal stability of the polymers, enabling  to iterate quickly and achieve the desired material characteristics."
            elif(scenario=="Green Chemistry"):
                t="Generate a list of potential compounds and environmentally benign synthesis methods.  monitor the reactions in real-time, ensuring that the processes minimize waste and energy consumption. Provide insights into the biodegradability and toxicity of the products, helping  develop a sustainable pesticide that meets regulatory standards and is safe for the environment."
    
            st.write("Generating Results..")
            prompt = t+target+constraints+stability
            response = send_message_to_model(prompt, impaths)
            st.write(response)


if __name__ == "__main__":
    main()