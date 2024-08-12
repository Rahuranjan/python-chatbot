
import time
from pymongo import MongoClient

import logging
from flask import Flask, jsonify, request
app = Flask(__name__)
from twilio.twiml.messaging_response import MessagingResponse
import pytesseract
from PIL import Image
from urlextract import URLExtract
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from datetime import datetime
                            

# Specify the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# app = create_app()

client = MongoClient('mongodb+srv://rahuranjan3455:WuyQ95xxOWMyArfB@cluster0.yjbj6ol.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client.get_database('subdomain')
collection = db.get_collection('hdfc')

if client is not None:
    print("Connected to MongoDB")



@app.route('/', methods=['GET'])
def hello():
    return "Hello, Good morning! "


INTELX_API_KEY = "13263d22-ba05-4e26-8edc-b37a581db363"
INTELX_API_URL = 'https://2.intelx.io/intelligent/search'
INTELX_RESULT_URL = 'https://2.intelx.io/intelligent/search/result'


@app.route('/search_intelx', methods=['POST', 'GET'])
def search_intelx():
    # Get the email from the request (support both POST and GET)
    # if request.method == 'POST':
    #     data = request.get_json()
    #     email = data.get('email')
    # else:
    #     email = request.args.get('email')

    email = "rahuranjan3455@gmail.com"
    
    # Check if the email parameter is provided
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400
    
    # Set up the headers with the API key
    headers = {
        'x-key': INTELX_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Set up the payload for the IntelX API request
    payload = {
        'term': email,
        'maxresults': 10  # Adjust the number of results as needed
    }

    try:
        # Make a POST request to the IntelX API
        response = requests.post(INTELX_API_URL, headers=headers, json=payload)
        
        # Debugging: Print response status and content
        print(f'Status Code: {response.status_code}')
        print(f'Response Content: {response.content.decode()}')

        # Check the response status code
        if response.status_code == 200:
            # Return the JSON response from the IntelX API
            return jsonify(response.json())
        elif response.status_code == 404:
            return jsonify({'message': 'No breaches found for this email.'}), 404
        else:
            # Return an error message if the request was not successful
            return jsonify({'error': 'Failed to search IntelX', 'details': response.content.decode()}), response.status_code
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return jsonify({'error': f'RequestException: {str(e)}'}), 500
    except Exception as e:
        # Handle any other exceptions
        return jsonify({'error': f'Exception: {str(e)}'}), 500


@app.route("/pdftext", methods=['GET'])
def pdf():
    text = extract_text('bank_domain.pdf')
    return jsonify(text)


@app.route("/subdomain", methods=['GET'])
def subdomain():
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    print(formatted_date)
    url = f"https://subdomainfinder.c99.nl/scans/2024-06-27/hdfcbank.com" 
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming subdomains are listed within <a> tags with a specific class or pattern
    subdomains = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and "hdfcbank.com" in href:
            subdomains.append(href)
        
    # Return the list of subdomains as a JSON response
    return jsonify(subdomains)


# @app.route("/getURL", methods=['GET'])
# def getURL():
#     if request.method == 'GET':
#         text = "Hi 968675xxxx, Your Loan Amount of Rs.983200/- has been Successfully Disbursed to Your Account. Withdraw Now 7ko4.com/vtgvro90m06mp either you can visit 1paytag.hdfcbank.com"
#         extractor = URLExtract()
#         urls = extractor.find_urls(text)
#         print(urls)
#         # Query MongoDB collection for matching subdomains
#         # matching_subdomains = collection.find({"subdomain": {"$in": urls}}, {"_id": 0, "subdomain": 1})

#         # Extract subdomains from matching documents
#         # matched_subdomains = [doc["subdomain"] for doc in matching_subdomains]

#         return jsonify(urls)

def getURL(text):
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    return urls



@app.route("/sms", methods=["GET", "POST"])
def reply():
    print(request.form)
    num = request.form.get('From').replace("whatsapp:", "")
    msg_text = request.form.get('Body')
    count_file = request.form.get('NumMedia')
    type123 = request.form.get('MediaContentType0')
    print(count_file)
    print(type123)
    
    msg = MessagingResponse()
    response = msg.message("I am ready to help you. Please share the text or image file so that I can tell you if the message is fake or not.")
    

    
    if count_file == '0':  # No media, assuming it's the first message or text
        if not msg_text:  # First message
            response = msg.message("I am ready to help you. Please share the text or image file so that I can tell you if the message is fake or not.")
            
        else:  # Text message
            # urls = getURL(msg_text)
            # msg.message(f"Extracted URLs: {urls}")
            # msg.message("share your email or phone to check is it pwned or not")
            pwned_message = check_mail(msg_text)
            print(pwned_message)
            response = msg.message(pwned_message)
    elif count_file == '1' and type123 and type123.startswith('image/'):  # Image file
        image_url = request.form.get('MediaUrl0')
        print("image url are", image_url)
        if image_url:
            text = scamtext(image_url)
            urls = getURL(text)
            response = msg.message(f"Extracted URLs: {urls}")
            response = msg.message(f"Extracted text from image: {text}")
        else:
            response = msg.message("Image URL not found in the request.")
    else:
        pwned_message = check_mail(msg_text)
        response = msg.message(pwned_message)


    return str(msg)


@app.route("/scamtext", methods=["get", "post"])
def scamtext(image_url):
    # Download the image from the URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    
    # Perform OCR
    text = pytesseract.image_to_string(image)
    print(text)
    return text


# @app.route("/check_email", methods=['GET', 'POST'])
def check_mail(email):
    print(email)
    # email = request.args.get('email')
    # email = "pushp2910@gmail.com"
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    payload = {
        'action': 'msp_pawned_callback',
        'emailAddress': email,
        'name': '',
        'nonceval': '757a8668d2',
        'noncekey': '070151a0-b1e4-4966-a7de-dd9633d20d5a',
        'agree': 'false'
    }

    try:
        response = requests.get('https://www.uptech.co.uk/wp-admin/admin-ajax.php', params=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

         # Check if the content type is HTML
        if 'text/html' in response.headers.get('Content-Type'):
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for panel in soup.find_all('div', class_='msp_pawned_panel'):
                h2 = panel.find('h2').get_text(strip=True)
                p = panel.find('p').get_text(strip=True)
                data = panel.find('p', class_="msp_breached").get_text(strip = True)
                results.append({'title': h2, 'description': p})

            result_messages = []
            for result in results:
                result_messages.append(f"Title: {result['title']}\n ")


            return "\n\n".join(result_messages)

        # Handle other unexpected content types
        else:
            return jsonify({'error': 'Unexpected content type'}), 500

    except requests.exceptions.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}'
    except requests.exceptions.RequestException as req_err:
        return f'Request error occurred: {req_err}'

if __name__ == '__main__':
    logging.info("Flask app is running.")
    app.run(debug=True, host="0.0.0.0", port=5001)

