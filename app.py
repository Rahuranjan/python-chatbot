
from pymongo import MongoClient

import logging
from flask import Flask, request
app = Flask(__name__)
from twilio.twiml.messaging_response import MessagingResponse
import pytesseract
from PIL import Image


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



@app.route("/sms",methods=["get","post"])
def reply():
    msg_text=request.form.get("Body")
    sen_num=request.form.get("From")
    sen_num=sen_num.replace("whatsapp:","")
    msg=MessagingResponse()
    response=msg.message("you send " +msg_text +" from :"+sen_num)
    response1=msg.message("total technology logolaslaSLakslaSLAksas")
    response1.media("https://i.ibb.co/YNt9yKb/Y7070-pp.jpg")
    return(str(msg))

@app.route("/scamtext", methods=["get", "post"])
def scamtext():
    # Open the image file
    image = Image.open('scammsg.jpeg')

    # Perform OCR using PyTesseract
    text = pytesseract.image_to_string(image)
    print(str(text))
    return (str(text))

if __name__ == '__main__':
    logging.info("Flask app is running.")
    app.run(debug=True, host="0.0.0.0", port=5001)

