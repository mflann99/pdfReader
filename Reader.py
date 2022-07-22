import PyPDF2
import re
import pandas as pd
import requests


PARCEL_REGEX = r"^.*(\b\d{2}-\d{2}-\d{3}-\d{3}-\d{4}\b)"
OWNERSHIP_REGEX = r"MAILING ADDRESS\n(.*)"
LOT_SIZE_REGEX = r"\bLot\sSize\s\(SqFt\):\s?(\S*)\b"
TAX_YEAR_REGEX = r"^{}:(\S*)"

ASSESSOR_REGEX = r"{type}.*?xs-{year}\">(\S*)<"

TAX_YEARS = ["2021","2020","2019","2018","2017"]
CURRENT_TAX_YEAR = 2021

ASSESSOR_HEADERS = ["Land Assessed Value","Building Assessed Value","Total Assessed Value"]

def read(fileName,pageNum):
    try:
        if(fileName[len(fileName)-3:len(fileName)] != "pdf"):
            raise ValueError("Selected files are not PDFs")
        
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

def read_html(parcel):
    parcelId = re.sub("\D", "", parcel) #removes all non digit ($ signs or commas)
    url = 'https://www.cookcountyassessor.com/pin/{}'.format(parcelId)
    r = requests.get(url)
    text = r.text.replace('\n', ' ').replace('\r', '') #delete line breaks for searching

    #quick way to get smaller text block. will need to be updated soon
    text = re.search(r".*container-fluid psuedo-table(.*?)small",text,re.MULTILINE).group(1)
    
    return text

def ass_search(text,row,year = CURRENT_TAX_YEAR): #ass search because it is funny
    num = 4
    #default is most recent assessment
    if (year==2020):
        num = 5

    for h in ASSESSOR_HEADERS:#maybe revise the var names
        try:
            value = re.search(ASSESSOR_REGEX.format(type=h,year=num),text,re.MULTILINE).group(1) # "xs-5" is 2020 value, "xs-4" would be 2021
            value = re.sub(r"[,$]","",value)
        except:
            value=0
        row.append(value)
    return row

def parcel_search(text):
    parcel = re.search(PARCEL_REGEX,text,re.MULTILINE).group(1)
    return parcel

def ownership_search(text):
    return re.search(OWNERSHIP_REGEX,text,re.MULTILINE).group(1)

def lot_search(text):
    lot = re.search(LOT_SIZE_REGEX,text,re.MULTILINE).group(1)
    lot = re.sub(",", "", lot) #removes all non digit ($ signs or commas)
    return lot #probably type cast to int

def tax_year_search(text,row):
    for year in TAX_YEARS:
        tax = re.search(TAX_YEAR_REGEX.format(year),text,re.MULTILINE).group(1)
        tax = re.sub(r"[,$]", "", tax)
        row.append(tax) #typecast int
    return row

def add(text,db):
    row = []
    parcel = parcel_search(text)
    row.append(parcel)
    row.append(ownership_search(text))
    row.append(lot_search(text))
    
    ass_search(read_html(parcel),row,2020)#Change to take year input

    row = tax_year_search(text,row)

    db.loc[len(db.index)] = row

    return db

def compile(pdf_list,column_names, year=CURRENT_TAX_YEAR):
    data = pd.DataFrame(columns=column_names)
    try:
       for pdf in pdf_list:
            text = read(pdf,0)
            data = add(text,data)

    except ValueError as ve:
        return ve
    return data

