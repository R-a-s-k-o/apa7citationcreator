from bs4 import BeautifulSoup
import requests, re
import pandas as pd
import datetime
from urllib.request import Request, urlopen, HTTPError
import time

"""
USAGE

The codes, get input from a excel file called input.
Make sure, your input & output location, check row 39 & 280
Input excel file should have column called INPUT, inputs should be underneath that column.
For website, just copy and paste it to input excel file.
If you cite a pdf file on the website, title of the text should be entered manually.
Code prints the url which includes pdf and asks to enter the title belong to it.
For scientific papers, doi of the paper should be copies. However, doi's format
should be like "/10.1186/s12917-017-0996-5" or "10.1186/s12917-017-0996-5".
For better understanding you can look at the input excel file that I shared.
The code creates a excel file called output which includes your citation.

"""


"""
NOTES

For websites, citation doesn't include authors and date accepted as it is unknonw(n.d)
Researchgate would be better if we control if input doi is identical to output doi
Researchgate blocks ip if there are too much requests

Efficiency of code can be increased by changing algorithm. For DOI, code requests data from
google for each website in the list Web_Site. Instead, it could google doi from the data it could 
detect which websites includes the doi. Thus, until google blocks our ip, more citations can be created.
"""

#######   INPUT FILE LOCATION   #######
#Data should be in a column called INPUT 
df = pd.read_excel("Desktop/input.xlsx")
########################################

n_of_rows = int(df["INPUT"].count())
date = datetime.datetime.now()

def PdfSite(title,c_number,date):
    Month = date.strftime("%B")
    Day = date.strftime("%d")
    Year = date.strftime("%Y")    
    citation = f"[{c_number}] {title}.(n.d.) Retrieved {Month} {Day}, {Year}, from {in_put}  "
    
    return citation

def WSite(in_put,c_number,date):    
    global df
    req = requests.get(in_put)
    title = BeautifulSoup(req.text, "html.parser").title.text
    Month = date.strftime("%B")
    Day = date.strftime("%d")
    Year = date.strftime("%Y")    
    citation = f"[{c_number}] {title}.(n.d.) Retrieved {Month} {Day}, {Year}, from {in_put}  "
    
    return citation

def GSearch(search,web_site):
    gsearch = "https://www.google.com/search?q="+search
    req = requests.get(gsearch)
    html_data = BeautifulSoup(req.text, "html.parser").text
    is_include = web_site in html_data
    return is_include

def R_Gate(search,web_site):
    s = "https://www.google.com/search?q="+search
    req = requests.get(s)
    href_tags = BeautifulSoup(req.text, "html.parser").find_all(href=True) 
    for a in href_tags:
        
        if web_site in a["href"] and "/url?q" in a["href"]:            
            x = a["href"][48:-1]
            
            for i in range(len(x)):
                if not x[i].isnumeric():
                    break
            id = x[0:i]

            url_start_with = "https://www.researchgate.net/lite.publication.PublicationDownloadCitationModal.downloadCitation.html?publicationUid=" 
            # BibTeX or Plain
            url_ends_with = "&fileType=Plain&citation=citation"
            search_url = url_start_with + id + url_ends_with

            req_1 = requests.get(search_url)
            soup_1 = BeautifulSoup(req_1.text,"html.parser")

            return  soup_1


def NGov(search,web_site):
    s = "https://www.google.com/search?q="+search
    req = requests.get(s)
    href_tags = BeautifulSoup(req.text, "html.parser").find_all(href=True)
    for a in href_tags:
        
        if web_site in a["href"] and "/url?q" in a["href"]:            
            x = a["href"][39:-1]
            for i in range(len(x)):
                if not x[i].isnumeric():
                    break
            id = x[0:i]
            
            starts_with = "https://pubmed.ncbi.nlm.nih.gov/"
            ends_with = "/citations/"
            search_url = starts_with + id + ends_with
            req_1 = requests.get(search_url)
            soup_1 = str(BeautifulSoup(req_1.text,"html.parser"))            
            Dict = eval(soup_1)     
            
            return  Dict["apa"]["orig"]

def SDirect(search,web_site):
    try:
        prefix_web_site = "/url?q=https://www."
        s = "https://www.google.com/search?q=" + search
        req = requests.get(s)
        href_tags = BeautifulSoup(req.text, "html.parser").find_all(href=True)
        

        for a in href_tags:        
            if prefix_web_site+web_site in a["href"]:
                
                for x in range(len(a["href"][61:-1])):
                    if a["href"][61+x] == "&":
                        id = a["href"][61:61+x]
                        break

                prefix_web = "https://www.sciencedirect.com/sdfe/arp/cite?pii="
                suffix_web = "&format=text/plain&withabstract=false"
                url = prefix_web + id + suffix_web
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                data = str(urlopen(req).read())
                data = data[2:-1]
                data_list = list(data.split("\\r\\n"))

                authors = data_list[0]
                title = data_list[1]
                journal = data_list[2]
                volume = data_list[3]
                year = data_list[4]
                pages = data_list[5]
                issn = data_list[6]
                doi = data_list[7]
                # authors, (year). Title. Journal, Volume, pages. Doi
                citation = f"{authors} ({year[0:-1]}). {title[0:-1]}. {journal} {volume} {pages[0:-1]}. {doi}"
                return citation
    except HTTPError as err:
        if err.code == 400:
            return "Http Error 400"


# springer should be coded again, there is indexing problems and some other paper includes
# citation of the paper we are looking for then it crashes.
def springer_(doi):
    # Some of the papers doesn't have ending pages it causs error!
    starts_with = "https://citation-needed.springer.com/v2/references/"
    ends_with = "?format=refman&flavour=citation"
    if doi[0] == "/":
        doi = doi[1:]

    url = starts_with + doi + ends_with
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        
        data = urlopen(req).read().splitlines()
        authors = []

        for x in range(len(data)):      
            
            if data[x].decode("UTF-8")[0:2] == "AU":        
                authors.append(data[x].decode("UTF-8")[6:])
            elif data[x].decode("UTF-8")[0:2] == "UR":
                doi = data[x].decode("UTF-8")[6:] 
            elif data[x].decode("UTF-8")[0:2] == "TI":
                title = data[x].decode("UTF-8")[6:] 
            elif data[x].decode("UTF-8")[0:2] == "PY":
                year = data[x].decode("UTF-8")[6:] 
            elif data[x].decode("UTF-8")[0:2] == "JO":
                journal = data[x].decode("UTF-8")[6:]
            elif data[x].decode("UTF-8")[0:2] == "VL": 
                volume = data[x].decode("UTF-8")[6:]
            elif data[x].decode("UTF-8")[0:2] == "SP":
                sp = data[x].decode("UTF-8")[6:] 
            elif data[x].decode("UTF-8")[0:2] == "EP":
                ep = data[x].decode("UTF-8")[6:] 
        pages = f"{sp}-{ep}"
        authors = str(authors)[1:-1].replace("'","")

        citation = f"{authors}, ({year}). {title}. {journal}, {volume}, {pages}. {doi}"
        return citation
    except HTTPError as err:
        if err.code == 404:
            #return NaN
            return "NaN"
    
    

c_number = 1
for x in range(n_of_rows):
    in_put = str(df["INPUT"].iloc[x])
    
 # Main control if the data is website/paper(doi)
    if in_put.lower().rfind("www") > -1 or in_put.lower().rfind("http") > -1:
    # variable.rfind("x") return -1 if variable doesnt include x
        if in_put.lower().endswith(".pdf"):
            #PDF
            print(in_put)
            title = input("Enter Title of Link Above: ")
            result = PdfSite(title,c_number,date)
            df.loc[df["INPUT"]== in_put,"citation"] = result            

            c_number = c_number + 1
            
        #Normal Website
        else:
            
            result = WSite(in_put,c_number,date)
            df.loc[df["INPUT"]== in_put,"citation"] = result             
            
            c_number = c_number + 1
            
            
 #DOI : Paper Side           
    else:
                
        Web_Sites = ["sciencedirect.com","researchgate.net","pubmed.ncbi.nlm.nih.gov","springer.com"]
              

        for web_site in Web_Sites:
            # Does sleep affect banning conditions by google ?
            # Test it!
            time.sleep(2)
            search = in_put
            print(search, web_site)

            if GSearch(search,web_site):
                
                
                if web_site == "researchgate.net":
                    str_result = str(R_Gate(search,web_site)) 
                    result = f"[{c_number}] {str_result} "
                    df.loc[df["INPUT"] == in_put,"citation"] = result.replace("&amp;","&")   
                    c_number = c_number + 1
                    break
                elif web_site == "pubmed.ncbi.nlm.nih.gov":
                    str_result = NGov(search,"nih.gov")
                    result = f"[{c_number}] {str_result} "
                    df.loc[df["INPUT"] == in_put,"citation"] = result.replace("&amp;","&") 
                    c_number = c_number + 1
                    break
                elif web_site == "sciencedirect.com":
                    str_result = SDirect(search,web_site)
                    result = f"[{c_number}] {str_result} "
                    df.loc[df["INPUT"] == in_put,"citation"] = result.replace("&amp;","&") 
                    c_number = c_number + 1
                    break
                elif web_site == "springer.com":
                    str_result = springer_(search)                                      
                    result = f"[{c_number}] {str_result} "
                    df.loc[df["INPUT"] == in_put,"citation"] = result.replace("&amp;","&")                    
                    c_number = c_number + 1
                    break
            else:
                 
                if web_site == Web_Sites[-1]:
                    df.loc[df["INPUT"] == in_put,"citation"] = f" [{c_number}] NaN: Couldn't be found in Google."
                    c_number = c_number + 1




#####  OUTPUTFILE LOCATION  #####
df.to_excel("Desktop/output.xlsx")
##################################
