import google.generativeai as genai

import PIL.Image

genai.configure(api_key="AIzaSyBPlLN0RvHJQlCB8mBFVzE0aHCQlX_HFVg")
client = genai.GenerativeModel('gemini-2.0-flash')

image = PIL.Image.open('./static/images/image2.png')

response = client.generate_content(
    contents=["Break down every position of my receipt also show how many times each producs is bought, containing name ,price only! PLEASE GIVE ONLY WHAT I REQUESTED AS A JSON FILE!!! The format of json should look like this:[{'name':'Tikka Chicken Slices','price':1.99,'quantity':1},{'name':Gem Lettuce,'price':0.89,'quantity':3}]", image]
)

print(response.text)