from google import genai
from google.genai import types

import PIL.Image

image = PIL.Image.open('./image2.png')

client = genai.Client(api_key="Api-key")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["Break down every position of my receipt also show how many times each producs is bought, containing name ,price only! PLEASE GIVE ONLY WHAT I REQUESTED AS A JSON FILE!!! The format of json should look like this:[{'name':'Tikka Chicken Slices','price':1.99,'quantity':1},{'name':Gem Lettuce,'price':0.89,'quantity':3}]", image])

print(response.text)