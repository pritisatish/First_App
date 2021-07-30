# import essential libraries
#  OCR engine code
from calendar import monthrange
from collections import Counter
from date_extractor import extract_dates
import datefinder
from dateparser.search import search_dates
import datetime
import filetype
import os
import pdf2image
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import random
import re
import regex
import sys
import logging
import json



#######################################################################################
## NEED TO CHANGE THESES TWO LINES TO MAKE IT WORK

# points to the directory where tesseract locates  [Usually if lib installed as Admin, then don't required]
try:
    # C:\Users\himanshu\AppData\Local\Tesseract-OCR\tesseract.exe change this to admin location of tesseract.
   # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

except:
    pass
# Go to the directory where the pdf/image file locates
cur_folder = os.path.split(os.path.split(os.getcwd())[1])[1]
print("Current folder: ", cur_folder)
if (cur_folder != 'data/BankStatements'):
#if (cur_folder != 'BankStatements'):

    try:
        #os.chdir('./data/BankStatements')
        os.chdir('data')
        os.chdir('BankStatements')


    except Exception:
        try:
            print("BankStatements Folder not found")
            sys.exit()
        except:
            pass

#path1 = "E:\Preethi.Patil\Mortgage_Project\Folder_files_study\Mortgage_project_sent_by_varunsir\14_howard_bank.pdf"



#######################################################################################

#path=r"C:\Users\preeti.patil\image1\data\BankStatements\09_chase.jpg"


path=r'C:\Users\preeti.patil\PycharmProjects\Mortgage_Project\ML_Pro\data\BankStatements\09_chase.jpg'
#path=r"C:\Users\preeti.patil\PycharmProjects\Mortgage_Project\Final_Project\data\BankStatements\Bank Statement Template 3 - TemplateLab.pdf"
#path= r"C:\Users\preeti.patil\PycharmProjects\Mortgage_Project\Final_Project\data\BankStatements\14_howard_bank_0001.jpg"
#path=r"C:\Users\preeti.patil\PycharmProjects\Mortgage_Project\Final_Project\data\BankStatements\14_howard_bank.pdf"

class ProcessOCR:
    ## common to all methods


    image = ''  # input by user
    kind = -1  # Two kind & for them 2 methods used. [0: bank statement and 1: payslip]
    ver_val = ''  # ac num or emp ID input by user for verification
    list_count = []  # store values to match with account number provided by user input
    bVerified = False  # True in case account number gets verified
    accuracy = 0  # show accuracy of account number
    bIsPDF = False  # if pdf file then True
    data = ''  # save ocr data

    # for amount
    currency = ''  # save currency to show in final result
    bNegative_Amt = False  # True in case any negative value is present in the amount list
    page_cnt = 0  # count page in pdf
    finalVal = 0.0  # the final value(ending balance/pay)

    # for date
    date_list = []  # store the dates detected
    final_date = []  # store final date values(2 items for duration for bank statements & 1 item for date for payslips)
    max_day = 0  # get maximum days in a month (in case single date is available in bank statement)

    # constructor with arguments
    def __init__(self, imageName='', imageKind=-1, val_to_verify='',
                 debug=False):  # image & method used as input parameters

        self.image = imageName
        self.kind = imageKind
        self.ver_val = val_to_verify
        self.list_count = []
        self.bVerified = False
        self.accuracy = 0
        self.bIsPDF = False
        self.data = ''
        self.currency = ''
        self.page_cnt = 0
        self.bNegative_Amt = False
        self.finalVal = 0.0
        self.date_list = []
        self.final_date = []
        self.max_day = 0

        #if not os.path.isfile('imageName'):
        if not os.path.isfile(path):
            try:
                print("No such file '%s'" % imageName)
                sys.exit()
            except:
                pass
        elif imageName == '' or imageKind == '-1' or val_to_verify == '':
            try:
                print(
                    "Enter all fields/args. 1.Image name, 2.Kind: 0(bank statement)/1(payslip) 3. Account number/Employee ID")
                sys.exit()
            except:
                pass
        #         self.retrieveData(imageName, val_to_verify.lower())
        #self.retrieveData(imageName, val_to_verify)
        self.retrieveData(path,'00000988081483')
        #self.retrieveData(path, '1234567890')


    @staticmethod
    # check single instance
    def getInstance(imageName='', kind=-1, val_to_verify='', debug=False):
        if not ProcessOCR.__instance:
            ProcessOCR.__instance = ProcessOCR(imageName, kind, val_to_verify, debug)
            return ProcessOCR.__instance

    @classmethod
    # get file details whether pdf or normal image
    def getFileInfo(self, imgName):
        bPDF_File = False
        fType = filetype.guess(imgName)
        if fType is None:
            try:
                print('Please select a proper file')
                sys.exit()
            except:
                pass
        elif fType.extension.lower() == 'pdf':
            bPDF_File = True

        return bPDF_File

    # get OCR data from image to retrieve info
    def getData(self, img):
        custom_oem_psm_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_string(img, lang='eng', config=custom_oem_psm_config)
        if (self.currency ==''):
            self.getCurrency(self.data)
            #self.getCurrency('$17,120.00')
            #self.getCurrency('$5,442.23')
        if (self.bIsPDF == True):
            try:
                if (os.path.isfile(img)):  # if pdf file for which we create temporary jpg file,
                    os.remove(img)  # then delete that temporary file
            except:
                pass
        return data

        ## Account_Number_Specific_Methods ##

    # process the file(pdf or image)
    def processFile(self, imgName):
        if self.bIsPDF == True:  # pdf
            images = convert_from_path(imgName, 500)
            for i, img in enumerate(images):
                n = random.randint(0, 35565)
                fname = os.path.splitext(imgName)[0] + '_' + str(n) + '.jpg'
                img.save(fname, "JPEG")
                self.image = fname
                self.data += ' ' + self.getData(fname)
        else:  # normal image
            self.data = self.getData(imgName)

            # verify input data(a/c number)

    def verify_input_data(self, ver_val_input, data_input):
        self.data_ver_00(ver_val_input, data_input)
        self.data_ver_01(ver_val_input, data_input)
        self.data_ver_02(ver_val_input, data_input)

    ### 0. if find exact match using above code with \bver_val\b then a/c no. is same
    def data_ver_00(self, ver_val_input, data_input):
        self.list_count.clear()
        input_var = '\\b' + ver_val_input + '\\b'
        self.list_count.extend(re.findall(input_var, data_input))
        if self.list_count:  # if(len(self.list_count)>0):
            self.bVerified = True
            self.accuracy = '100%'

    ### 1. else search for normal findall(sometimes merge with other strings
    def data_ver_01(self, ver_val_input, data_input):
        if self.bVerified == False:  # if not account_number:
            self.list_count.clear()
            self.list_count.extend(re.findall(ver_val_input, data_input))
            if self.list_count:
                #bverified----account nbr of customer
                self.bVerified = True
                self.accuracy = '90%'

    ### 2. else if space is there in ac number, then remove and search in case exact match not found in 1st approach. Then search using 1st else 2nd way
    def data_ver_02(self, ver_val_input, data_input):
        if self.bVerified == False:
            if (data_input.find(' ') != -1):
                self.list_count.clear()
                ver_val_input = ver_val_input.replace(' ', '', -1)
                self.list_count.extend(re.findall(ver_val_input, data_input))
                if self.list_count:
                    self.bVerified = True
                    self.accuracy = '90%'
                else:  # try the new value using first two methods
                    self.data_ver_00(ver_val_input, data_input)
                    self.data_ver_01(ver_val_input, data_input)
                    ### work later on/concurrently

    #     ### 3. else replace few characters with few elements like 0 to o  MAKE DATA LOWERCASE WHILE PROCESSING
    #     def data_ver_03(self, ver_val_input, data_input):
    #         if self.bVerified == False:   ### if not verified then only proceed
    #             print("try final one replace 9 by $ 0 by o etc [ BUT ALL LOWERCASE AS WE HAVE CONVERTED DATA INTO THAT]")

    ## Date_Specific_Methods ##

    # get file details for extracting date
    def getCorrectFileType(self, pdfImg):
        self.getFileInfo(pdfImg)
        if self.bIsPDF == True:
            images = convert_from_path(pdfImg, 500)
            for i, img in enumerate(images):
                n = random.randint(0, 35565)
                fname = os.path.splitext(pdfImg)[0] + '_' + str(n) + '.jpg'
                img.save(fname, "JPEG")
                self.image = fname
                if (i == 0):  # current logic for 1 page only. discuss and extend later on
                    break;

    # get the maximum value of day(dd in dd/mm/yy) in the date list after processing image
    def getMaxDay(self, date_list):
        self.max_day = 0
        dd = []
        for i in date_list:
            dd.append(i.day)
        if dd:
            self.max_day = max(dd)
            if (self.max_day > 31):
                self.max_day = 0

                # dates retrieved using extract_dates and after filtering inserted into date list

     #extract_dates(data) ------data = it can be text or date
    def getInitialDateList(self, data):
        now = datetime.datetime.now()
        dates = extract_dates(data)
        date_list_00 = []  # for saving all dates

        if dates != [None]:
            for dt in dates:
                if dt != None:
                    year1 = int(dt.year)
                    year2 = int(now.year)
                    if (dt.date() > now.date()):
                        continue
                        # in final build put just 1 condition: check for latest(max last 2 years):
                    # if(year1 <= year2 and year1 >= year2-2):
                    if data.lower().find('chase') != -1:
                        if ((
                                year1 <= year2 and year1 >= year2 - 2) or year1 == 2008):  # Chase bank has year 2008 statement
                            date_list_00.append(dt)     #returns date_list----


                    elif data.lower().find('howardbank') != -1:
                        if ((
                                year1 <= year2 and year1 >= year2 - 2) or year1 == 2018):  # Howard bank has year 2018 statement
                            date_list_00.append(dt)
                    elif (year1 <= year2 and year1 >= year2 - 2):  # last two years (it should be used as used in banks)
                        date_list_00.append(dt)
        self.getMaxDay(date_list_00)
        if len(date_list_00) == 0:  # no date is founded
            self.date_list = date_list_00
            self.final_date.clear()
        elif (len(date_list_00) == 1):  # just 1 date is founded
            day = date_list_00[0].day
            end_date = monthrange(date_list_00[0].year, date_list_00[0].month)[1]  # get last date of month
            if (day == 1):  # 1st of month
                date_00 = date_list_00[0]  # set last day of month as last
                date_00 = date_00.replace(day=end_date)
                dt = datetime.datetime.combine(date_00, datetime.datetime.min.time())
                date_list_00.append(dt)
                # elif(day >= 28 and day <= 31):
            elif day >= 15:  # update later. end date can be different. e.g. 14_howard_bank_0001.jpg where it is 21/07/2018
                date_00 = date_list_00[0]
                date_00 = date_00.replace(day=1)
                dt = datetime.datetime.combine(date_00, datetime.datetime.min.time())
                date_list_00.append(dt)
        self.date_list = date_list_00

        # generate a final date list from initial one and retrieve final two lates dates

    def getFinalDateList(self, date_list):
        date_list_00 = date_list
        date_list_01 = []  # for retrieving correct dates

        if len(date_list_00) != 0:
            for i in date_list_00:
                for j in date_list_00:
                    if len(date_list_01) == 2:  # as just two final dates should be there
                        break
                    tot_day = i.date() - j.date()
                    days = tot_day.days
                    # if (days >= 27 and days <= 30):
                    if (
                            days >= 14 and days <= 30 and i.day >= self.max_day):  # for 14_howard_bank_0001 & 15_howard_bank_0001
                        bExist = i in date_list_01
                        if bExist == False:
                            date_list_01.append(i)
                        bExist = j in date_list_01
                        if bExist == False:
                            date_list_01.append(j)
                if len(date_list_01) == 2:  # as just two final dates should be there
                    break
        if len(date_list_01) == 2:  # now get two dates
            if date_list_01[1].date() > date_list_01[0].date():  # in case second date is greater than 1st. e.g. 21st March > 1st March
                self.final_date.extend(
                    (date_list_01[0].date(), date_list_01[1].date()))  # then insert in final date in correct order
            else:
                self.final_date.extend((date_list_01[1].date(), date_list_01[0].date()))
        else:  # if not get 2 dates
            date_list_01 = []
            b_BeginExist = False
            b_EndExist = False
            begin_date = datetime.datetime.now()  # get current time and check whether the date we get is greater than that for verification
            end_date = begin_date
            if len(date_list_00) != 0:
                for i in date_list_00:
                    if i.day == 1:
                        b_BeginExist = True
                        begin_date = i
                    # elif i.day >= 28 and i.day <= 31:
                    elif i.day >= 15:  # end date can be differente.g. 14_howard_bank_0001.jpg where it is 21/07/2018
                        b_EndExist = True
                        end_date = i
            if b_EndExist == True:  # in case end date found, we set other date as 1st
                date_00 = end_date
                date_00 = date_00.replace(day=1)
                dt = datetime.datetime.combine(date_00, datetime.datetime.min.time())
                date_list_01.append(dt)
                date_list_01.append(end_date)
            elif b_BeginExist == True:  # if 1st date is found, we get max days in the month and set that as end date
                end_date = monthrange(date_list_00[0].year, date_list_00[0].month)[1]  # get last date of month
                # date_00 = date_list_00[0] #set last day of month as last
                date_00 = begin_date
                if end_date < self.max_day:
                    end_date = self.max_day
                date_00 = date_00.replace(day=end_date)
                dt = datetime.datetime.combine(date_00, datetime.datetime.min.time())
                date_list_01.append(begin_date)
                date_list_01.append(dt)
            if len(date_list_01) == 2:  # if finally get two elements using above technique
                if date_list_01[1].date() > date_list_01[0].date():
                    self.final_date.extend((date_list_01[0].date(), date_list_01[1].date()))
                else:
                    self.final_date.extend((date_list_01[1].date(), date_list_01[0].date()))
            else:
                self.final_date.clear()  # otherwise no date

    # for monthly employee payslip
    #parameter,data=
    def getFinalDate(self, data):
        li = list(data.split(" "))
        date_list_0 = []  # search_dates method and then datefinder [cover all dates]
        date_list_1 = []  # datefinder [look up for correct date if in lib's specified formats in data]
        now = datetime.datetime.now()
        print("inside getFinalDate")
        for item in li:
            dates = search_dates(item)  # here we use search_dates lib method followed by find_dates
            if dates != None:
                for dt in dates:
                    date_string = dt[0]
                    val = datefinder.find_dates(date_string)
                    for i in val:
                        # if i <= now and i.year >= now.year-2: #use this one in final release as max last 2 years
                        if (i <= now) and (i.year >= now.year - 10):  # this used here for covering all files here
                            date_list_0.append(i.date())
            val = datefinder.find_dates(item)
            for i in val:  # and then filter by verifying date
                if i != None:
                    # if i <= now and i.year >= now.year-2: #use this one in final release as max last 2 years
                    if (i <= now) and (i.year >= now.year - 10):  # this used here for covering all files here
                        date_list_1.append(i.date())
        if (len(date_list_1) == 1):  # in case search_dates and find_dates value match(exact match)
            self.final_date.extend(date_list_1[0])
        elif (len(
                date_list_0) == 1):  # value we get in using search_dates  #just 1 value taken as 1 date is there in payslip
            self.final_date.extend(date_list_0[0])
        else:
            self.final_date.clear()

            ## Amount_Specific_Methods ##

    # retrieve the currency
    #dataVal= the string which got converted from image
    def getCurrency(self, dataVal=''):
        exp = "\\p{Sc}"
        cur_list = regex.findall(exp, dataVal)
        if cur_list:
            self.currency = max(cur_list, key=cur_list.count)

            # get list with amount data in float format from file

    def getAmtList(self, data):
        exp = '\-{0,1}\s{0,1}\p{Sc}{0,1}\d+\,{0,1}\d*\,{0,1}\d*\,{0,1}\d*\,{0,1}\d*\.\d\d'  # \p{Sc} used for any currency sign
        amount_list_temp = regex.findall(exp, data)
        formatted_page_list = []  # to save in float format removing all symbols,spaces,currency symbols
        for amt in amount_list_temp:
            amt = regex.sub('[,\s\p{Sc}]', '', amt)
            if float(amt) < 0:  # if -ve val present
                self.bNegative_Amt = True
            formatted_page_list.append(float(amt))
        formatted_page_list = list(
            filter(lambda x: int(x) != 0, formatted_page_list))  # remove zeros since no significance
        return formatted_page_list

        # Get final pay as it is present in the last

    def getFinalPayVal(self, data):
        lst = self.getAmtList(data)
        if lst:
            self.finalVal = lst[-1]

    # retrieve final balance value comparing max occurance val with first page val
    def getFinalBalVal(self, amount_list, first_page_list):
        if amount_list:
            max_occur_val = max(amount_list, key=amount_list.count)
            self.finalVal = 0.00
            while (len(amount_list) > 0):
                max_occur_val = max(amount_list, key=amount_list.count)
                if max_occur_val in first_page_list:
                    self.finalVal = max_occur_val
                    break
                amount_list = list(filter((max_occur_val).__ne__,
                                          amount_list))  # remove that element & look for next most occuring element

    # get Balance Data
    def processBal(self, Img):
        if self.bIsPDF == True:  # pdf
            images = convert_from_path(Img, 500)
            amount_list = []
            first_page_list = []  # to check if final value we get is present in first page
            data_temp = ''
            self.data = ''
            for i, img in enumerate(images):
                n = random.randint(0, 35565)
                fname = os.path.splitext(Img)[0] + '_' + str(n) + '.jpg'
                img.save(fname, "JPEG")
                self.image = fname
                data_temp = self.getData(fname)
                self.data += data_temp + ''
                lst = self.getAmtList(data_temp)
                amount_list.extend(lst)
                if (i == 0):  # save amount list data for first page
                    first_page_list.extend(lst)
            self.getFinalBalVal(amount_list, first_page_list)
        else:  # normal image
            amount_list = []
            lst = self.getAmtList(self.data)
            amount_list.extend(lst)
            itr = len(amount_list) - 1  # total iterations
            final_amt = 0.00

            if (itr == -1 or itr == 0):  # no/one element found
                final_amt = 0.00
            elif (itr == 1):  # two elements
                final_amt = amount_list[1]  # Second Value as Ending Balance comes in second position
            elif (self.bNegative_Amt == True):
                bFirst_Neg = False  # True in case find first negative value
                tot = 0.00
                i = 0  # for iterations. till last -1 element as we need to compare it with
                for amt in amount_list:
                    i += 1
                    if amt < 0 and bFirst_Neg == False:
                        bFirst_Neg = True
                        tot = amount_list[i - 3] + amount_list[i - 2] + amt  # i.beginning  ii.in  iii.out
                    elif bFirst_Neg == True:
                        if tot == amt:
                            final_amt = tot
                            break
                        else:
                            tot += amt
            elif (self.bNegative_Amt == False and len(
                    amount_list) > 3):  # if no negative value & more than 3 amounts in list.
                tot = amount_list[0] + amount_list[1] - amount_list[2]  ##ending balance: input + in - out
                if tot == amount_list[3]:
                    final_amt = tot
            self.finalVal = final_amt

    ## Common_To_All ##
    # get output in desired format
    # val='-'
    def getOutput(self, val='-'):
        output = "-"
        # ac_number/emp ID
        if (self.bVerified == False):

            if self.kind == 0:  # bank statement
                try:
                    raise Exception("Customer account number verification failed")
                except Exception:
                    logging.exception("Logging Error with not entering correct account number")
                    raise
                # print("Customer account number verification failed")
                # sys.exit()
            else:  # payslip
                #output = "Employee number/ID verification failed."
                try:
                    raise Exception("Employee number/ID verification failed.")
                except Exception:
                    logging.exception("Logging Error with with not entering correct Employee number/ID")
                    raise

        else:
            if self.kind == 0:  # bank statement
                output = "Account Number: {0} verified with accuracy: {1}".format(self.ver_val, self.accuracy)
            else:  # payslip
                output = "Employee Number/ID: {0} verified with accouracy: {1}".format(self.ver_val, self.accuracy)
        print(output)
        # duration
        if self.final_date:
            if self.kind == 0:  # bank statement
                ouput= "Time Span: {0} to {1}".format(self.final_date[0], self.final_date[1])
            else:  # payslip
                ouput = "Time Span: {0} to {1}".format(self.final_date[0])
        else:  # no data retrieved
            if self.kind == 0:  # bank statement
                output = "Unable to find account statement period."
            else:  # payslip
                output = "Unable to find payment date."
        print(ouput)
        # closing balance/payment
        if (int(val) == 0):
            if self.kind == 0:  # bank statement
                output = "Unable to find closing balance."
            else:  # payslip
                output = "Unable to find payment amount."
        else:
            before, after = str(val).split('.')
            before = int(before)
            after = int(after[:2])
            if self.kind == 0:  # bank statement
                ouput = "Closing Balance: {0}{1}{2}{3}".format(self.currency, f'{before:,}', '.', after)
            else:  # payslip
               ouput = "Final Payment: {0}{1}{2}".format(f'{before:,}', '.', after)
        print(ouput)

        ## Final_Function_Called_At_Object_Initialization ##

    def retrieveData(self, img, val_input):
            self.bIsPDF = self.getFileInfo(path)
            # self.bIsPDF = self.getFileInfo(img)
            self.processFile(path)  # Amount Number Section
            # self.processFile(img)

            # self.verify_input_data(val_input, self.data)  # Amount Number Section
            # self.verify_input_data(val_input,'00000988081483')
            self.verify_input_data(val_input, '00000988081483')
            # self.verify_input_data('00000988081483', '00000988081483')
            # self.verify_input_data('00000988081483', self.data)

            self.image = img
            self.getCorrectFileType(path)
            # data = self.getData(self.image)
            data = self.getData(path)  # data-----ocr data which is extracte from image

            if (self.kind == 0):  # for bank statement file
                self.getInitialDateList(data)
                if (len(self.date_list) != 0):
                    self.getFinalDateList(self.date_list)  # Balancesheet Period
                self.processBal(path)  # Account Balance Section
            elif self.kind == 1:  # for payment slip file
                # self.getFinalDate("July 1,2008")
                # self.getFinalDate("July 31,2008")
                self.getFinalDate(data)  # Payslip Date
                self.getFinalPayVal(self.data)  # Final Payment Section
            self.getOutput(self.finalVal)  # display output correctly


output = ProcessOCR(path,0)
