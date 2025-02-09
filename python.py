from google import genai
from google.genai import types

import PIL.Image

image = PIL.Image.open('./image.png')

client = genai.Client(api_key="API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["What is this image? Break down every position also show how many times each producs is bought, containing name ,price only and the lowes and highest price of an item! PLEASE GIVE ONLY WHAT I REQUESTED AS A JSON FILE!!! ALSO can you findcheaper alternatives to each item from uk supermarket stores", image])

print(response.text)