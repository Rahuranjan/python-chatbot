
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
import fitz


# Specify the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# app = create_app()

client = MongoClient('mongodb+srv://rahuranjan3455:WuyQ95xxOWMyArfB@cluster0.yjbj6ol.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client.get_database('subdomain')
collection = db.get_collection('hdfc')

if client is not None:
    print("Connected to MongoDB")



   
# Extract text from the PDF file




import requests



@app.route('/', methods=['GET'])
def hello():
    return "Hello, Good morning! "

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    with fitz.open(pdf_path) as doc:
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
    return text


@app.route("/pdftext", methods=['GET'])
def pdf():
    pdf_path = 'bank_domain.pdf'
    text = extract_text_from_pdf(pdf_path)
    return jsonify({"text": text})


@app.route("/subdomain", methods=['GET'])
def subdomain():
    url = "https://subdomainfinder.c99.nl/scans/2024-06-30/hdfcbank.com"    
    # need to change date(current date and domain) and bank doamin (get it from bank_doamin pdf)
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
    
    if count_file == '0':  # No media, assuming it's the first message or text
        if not msg_text:  # First message
            response = msg.message("I am ready to help you. Please share the text or image file so that I can tell you if the message is fake or not.")
        else:  # Text message
            urls = getURL(msg_text)
            response = msg.message(f"Extracted URLs: {urls}")
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
        response = msg.message("Please send either a text message or a single image file.")

    return str(msg)

image_url = "https://api.twilio.com/2010-04-01/Accounts/ACe45aa633376491968426bda66f570c15/Messages/MM512b4bad3cedbd71b45a09f8f1799c7e/Media/MEf0f785859911c97ccf0301e6749fbec2"

@app.route("/scamtext", methods=["get", "post"])
def scamtext(image_url):
    # Download the image from the URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    
    # Perform OCR
    text = pytesseract.image_to_string(image)
    print(text)
    return text

if __name__ == '__main__':
    logging.info("Flask app is running.")
    app.run(debug=True, host="0.0.0.0", port=5001)

