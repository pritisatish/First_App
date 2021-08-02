#flask server
from flask import Flask, render_template, request,redirect,url_for
from main import ProcessOCR
from main import *
from werkzeug.datastructures import FileStorage
# import our OCR function

# define a folder to store and later serve the images
#UPLOAD_FOLDER = '/static/uploads/'
UPLOAD_FOLDER = r"E:\Preethi.Patil\image1\file_upload"

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

app = Flask(__name__)

#filename= r'C:\Users\preeti.patil\PycharmProjects\Mortgage_Project\ML_Pro\data\BankStatements\09_chase.jpg'

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route and function to handle the home page
@app.route('/')
def home():
    #return render_template('index.html')
    return '<h1>welcome,App</h1>'

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':

        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('display.html', msg='No file selected')

        file = request.files['file']
        if file.filename == '':
            return render_template('display.html', msg='No file selected')

        if file and allowed_file(file.filename):

            select = request.form.get('Banks')
            # input = allowed_file(file.filename)
            f = FileStorage(filename=file.filename)
            input = f.filename

            print(select)
            print(input)
            if (select == 'sample-chase' and input == '09_chase.jpg'):

                result = ProcessOCR(input, 0)

        else:
            return "Invalid Account Number"



        return render_template('display.html',
                                       #msg='Successfully processed',
                                       #extracted_text=msg,extracted_text1=result.final_date,extracted_text2=result.final_val,
                                       extracted_text=result.accuracy,extracted_text1=result.final_date,extracted_text2=result.finalVal,

                                       img_src=UPLOAD_FOLDER + file.filename)

    elif request.method == 'GET':
        return render_template('display.html')


if __name__ == '__main__':
    app.run(debug=True)