from time import sleep
import requests, os, re
from bs4 import BeautifulSoup
from requests.utils import quote
import zipfile

LOGIN_URL = 'https://gate.meteoswiss.ch/idaweb/login.do'
STATION_WIZARD_URL = 'https://gate.meteoswiss.ch/idaweb/system/orderWizard.do?method=station'
STATION_URL = "https://gate.meteoswiss.ch/idaweb/system/stationList.do"
PARAMETERS_URL = "https://gate.meteoswiss.ch/idaweb/system/parameterList.do"
CRITERIA_URL = "https://gate.meteoswiss.ch/idaweb/system/criteria.do"
INVENTORY_URL = "https://gate.meteoswiss.ch/idaweb/system/inventoryList.do"
ORDER_URL_POST = "https://gate.meteoswiss.ch/idaweb/system/order_v.do"
AGB_URL = "https://gate.meteoswiss.ch/idaweb/system/agb_v.do"

email = "katarina.fatur%40students.fhnw.ch"
password = "7CDB6F8990"


def scrape_data(email, password, start_date, end_date):
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

    # Login
    session.get(LOGIN_URL)
    session.post(LOGIN_URL, data="method=validate&user=" + email + "&password=" + password)

    # Stationenportal
    session.get(STATION_WIZARD_URL)

    # Stationsvorwahl
    session.post(STATION_URL, data="method=step&state=parameter&showPreseletion=false&"
                                   "selection=401&"  # ABV 
                                   "selection=409&"  # BIV
                                   "selection=832&"  # GUS 
                                   "selection=468&"  # LAT
                                   "selection=539&"  # PON 
                                   "selection=224&"  # SAN
                                   "selection=30&"  # SCU
                                   "selection=344&"  # SDO
                                   "selection=215&"  # SED
                                   "selection=629&"  # SLF5OB
                                   "selection=213&"  # SLF5SE
                                   "selection=340&"  # SLF5VA
                                   "selection=583&"  # SLF7MA
                                   "selection=585&"  # SLF7MZ
                                   "selection=5019&"  # SLF7SU 
                                   "selection=600&"  # SLF7ZU
                                   "selection=25&"  # SMM
                                   "selection=1120&"  # SMZ
                                   "selection=1200&"  # SPL
                                   "selection=465&"  # SVG
                                   "selection=638&"  # TST
                                   "selection=947&"  # VEL
                                   "canton=&name=&natAbbr=&height=&kmCoordX=&kmCoordY=&longitude=&latitude=&macro=")

    # Parametervorwahl
    session.post(PARAMETERS_URL,
                 data="method=step&state=criteria&showPreseletion=false&"
                      "selection=939&"  # Schneehöhe; Jahresmittel
                      "selection=938&"  # Schneehöhe; Monatsmittel
                      "paramGroup=&name=&shortName=&granularity=all&unit=--+alle+--&macro=0")

    # Zeitvorwahl
    session.post(CRITERIA_URL, f"method=step&ignoreWarnings=false&state=inventory&showPreseletion=false&"
                               f"since={start_date}&"
                               f"till={end_date}")

    # Messdateninventar
    inventory_response = session.post(INVENTORY_URL, "method=selectAll&state=unspecified&showPreseletion=false&"
                                                     "stationName=&paramName=&paramGranularity=D&paramUnit=--+alle+--")

    inventory_soap = BeautifulSoup(inventory_response.text, features="html.parser")
    inventory_values = [f"&selection={quote(x['value'])}" for x in inventory_soap.find_all("input", type="checkbox")]
    session.post(INVENTORY_URL, f"method=step&state=order&showPreseletion=false{''.join(inventory_values)}"
                                f"&stationName=&paramName=&paramGranularity=D&paramUnit=--+alle+--")

    # Bestellung konfigurieren
    session.post(ORDER_URL_POST, f"method=step&ignoreWarnings=false&state=summary&showPreseletion=false&"
                                 f"orderText={start_date}-{end_date}&dataFormat=data.format.csv&plInfo=on&muInfo=on")

    # Extract 'struct' token
    agb_response = session.get("https://gate.meteoswiss.ch/idaweb/system/agb.do")

    agb_soap = BeautifulSoup(agb_response.text, features="html.parser")
    token = agb_soap.find("input", {"name": "org.apache.struts.taglib.html.TOKEN"})["value"]

    session.post(AGB_URL, "org.apache.struts.taglib.html.TOKEN=" + token +
                 "&method=enable&ignoreWarnings=false&state=unspecified&showPreseletion=false&acceptAgbs=on")
    summary_response = session.post(AGB_URL, "org.apache.struts.taglib.html.TOKEN=" + token +
                                    "&method=order&ignoreWarnings=false&state=unspecified&"
                                    "showPreseletion=false&acceptAgbs=on")

    # Extract the download link.
    summary_soap = BeautifulSoup(summary_response.text, features="html.parser")
    download_url = summary_soap.find('a', text="Lieferschein")["href"][:-4]

    # Data is not available immediately.
    sleep(90)
    data_download = session.get(download_url)

    # Write response to a zip file.
    file_name = 'raw_data.zip'
    file = open(file_name, 'wb')
    file.write(data_download.content)
    file.close()

    # unzip zip file

    #     cwd = os.getcwd()
    #     regex = re.compile('(.*zip$)')
    #     for root, dirs, files in os.walk(cwd):
    #         for file in files:
    #             if regex.match(file):
    #                 print(file)
    #                 with zipfile.ZipFile(file,"r") as zip_ref:
    #                     zip_ref.extractall()
    #                 os.remove(file)

    # There is no need to search for the file with os.walk since we statically named the file 'raw_data.zip'
    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall()

    # Since we already know the name of the file we can remove it directly.
    os.remove(file_name)
