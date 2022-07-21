import PyPDF2
import re
import pandas as pd
from pyparsing import col

FILE_NAME = "tax.pdf"
PAGE_NUMBER = 0

COLUMN_NAMES = ["Parcel ID","Lot Size","2021 tax","2020 tax","2019 tax","2018 tax","2017 tax"]

PARCEL_REGEX = ".*(\b\d{2}-\d{2}-\d{3}-\d{3}-\d{4}\b)"
LOT_SIZE_REGEX = "\bLot\sSize\s\(SqFt\):\s?(\S*)\b"

TAX_YEARS = ["2021","2020","2019","2018","2017"]


def read(fileName,pageNum):
    try:
    #tax.pdf for name of pdf
        pdffileobj=open(fileName,'rb')
        pdfreader=PyPDF2.PdfFileReader(pdffileobj)
 
        #This will store the number of pages of this pdf file
        x=pdfreader.numPages
 
        #create a variable that will select the selected number of pages
        pageobj=pdfreader.getPage(pageNum)
 
        text=pageobj.extractText()

    except:
        text = "error"

    return text

def add(text,db):
    row = []
    #Parcel regex search
    parcel = re.search(r"^.*(\b\d{2}-\d{2}-\d{3}-\d{3}-\d{4}\b)",text,re.MULTILINE).group(1)
    row.append(parcel)
    #lot size regex search(sqft)
    lot = re.search(r"\bLot\sSize\s\(SqFt\):\s?(\S*)\b",text,re.MULTILINE).group(1)
    lot = re.sub("\D", "", lot) #removes all non digit ($ signs or commas)
    row.append(lot)

    for year in TAX_YEARS:
        tax = re.search(r"^{}:(\S*)".format(year),text,re.MULTILINE).group(1)
        tax = re.sub("\D", "", tax)
        row.append(tax)

    db.loc[len(db.index)] = row

    return db

def compile(pdf_list):
    data = pd.DataFrame(columns=COLUMN_NAMES)
    try:
       for pdf in pdf_list:
            text = read(pdf,0)
            data = add(text,data)
    except:
        print("compile error")
    return data

text = read("tax2.pdf",0)
# print(text)
data = compile(["tax.pdf","tax2.pdf"])
print(data.head(2))
