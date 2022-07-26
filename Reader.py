import PyPDF2
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


PARCEL_REGEX = r"^.*(\b\d{2}-\d{2}-\d{3}-\d{3}-\d{4}\b)"
OWNERSHIP_REGEX = r"MAILING ADDRESS\n(.*)"
LOT_SIZE_REGEX = r"\bLot\sSize\s\(SqFt\):\s?(\S*)\b"
TAX_YEAR_REGEX = r"^{}:(\S*)"

#ASSESSOR_REGEX = r"{type}.*?xs-{year}\">(\S*)<"

TAX_YEARS = ["2021","2020","2019","2018","2017"]
CURRENT_TAX_YEAR = 2021


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
    parcelId = re.sub("\D", "", parcel)
    try:
        url = 'https://www.cookcountyassessor.com/pin/{}'.format(parcelId)
        r = requests.get(url)
        scraper = BeautifulSoup(r.content, "html.parser")
        #only takes the assessed valuation portion of the full assessor website
        #can much more easily be changed to do other categories than last implementation
        results = scraper.find_all("div", {"class": "row pt-body equal-height"})
        return results[1:4]
    except:
        print("Error: html not read properly")
        return "" #error stemming from not finding correct html table
    

def ass_search(cells,row,year = CURRENT_TAX_YEAR):
    try:
        year_index=4 #default code is current year
        if year == 2020:
            year_index = 5 # signifies last years assessed values
        for cell in cells:
            value = cell.find("div", class_=f"col-xs-{year_index}")
            value = re.sub(r"[,$]","",value.text)
            row.append(value)
        return(row)
    except:
        print("Error: proper values not found")
        return []
        

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

def add(text,db,year):
    row = []
    parcel = parcel_search(text)
    row.append(parcel)
    row.append(ownership_search(text))
    row.append(lot_search(text))
    
    ass_search(read_html(parcel),row,year)#Change to take year input

    tax_year_search(text,row)

    db.loc[len(db.index)] = row

    return db

def compile(pdf_list,column_names, year=CURRENT_TAX_YEAR):
    data = pd.DataFrame(columns=column_names)
    try:
       for pdf in pdf_list:
            text = read(pdf,0)
            data = add(text,data,year)
    except ValueError as ve:
        return ve
    return data

