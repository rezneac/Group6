# Save Smart by Group 6

Plan smarter, spend happier with SaveSmart.

## Group Members
Ross Watts - rw360@student.le.ac.uk
Emmanuel Ekhator - efe1@student.le.ac.uk
Shreya Chudasama - sc973@student.le.ac.uk
Anatolie Rezneac - ar684@student.le.ac.uk
Neha Karia - nhk6@student.le.ac.uk

## Installation

Our application is a flask web app which uses the Google Gemini API.

1. Obtain an API key from: https://aistudio.google.com/app/apikey. Then create a file called `.env` containing:
```
API_KEY=<your-api-key>
```

Where \<your-api-key\> is replaced with that API key.

2. To install the required python packages run:
```bash 
python -m pip install -r requirements.txt
```

3. Then to run the application:
```bash
python app.py
```

### Other scripts

To reset the database, delete the file `instance/database.db` and run:
```bash
python database.py
```

`python.py` contains a script to interact with the Google Gemini API.

`seatch_product_parser.py` contains a web scraper which searches `trolley.co.uk` for cheaper grocery alternatives. This could be used to improve the accuracy of our cheaper product suggestions.

