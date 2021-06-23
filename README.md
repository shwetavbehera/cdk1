# Challenge Klimadaten 2021
This is the repository for Challenge Klimadaten.

We created a web dashboard to display snow data from Graubunden ski locations.

The dashboard is created in **Dash**, for visualization we use **Plotly**, we scrape data using the **requests** and 
**BeautifulSoup4** libraries.

The database connection is handled by **Psycopg2**. Further libraries are used to handle files, expressions, system operations and more.


## Needed libraries

You need the following libraries:

- dash
- plotly
- pandas
- glob
- requests
- BeautifulSoap4
- requests
- re
- psycopg2
- io
- os
- time 
- datetime
- sys
- zipfile

## Project overview

- app.py - Dash webapp dashboard. Start to run server locally.
- database.py - Data processing functions for graphs.
- initial_download.py - Initial download, wrangle and import of data into SQL.
- monthly_download.py - Monthly data scrape, wrangle and insert new data into PostgreSQL DB hosted by ElephantSQL.
- assets/ - Images for HTML.
- data_story/ - Resources for data story.
- explorative_analysis/ - Initial explorative analysis files.

The webapp is composed by 5 components:

- WebApp
- Database
- Initial download
- Monthly scraping
- Datawrangler

## How to run the WebApp

Open Windows command prompt by typing cmd and pressing enter in the start menu.
Use **cd** to go to project folder and run **python app.py**.

## Database

The database consists of one Table and 2 main attrubutes (ignoring columns like time and names). It gets its data from an initial bulk load of data (import of csv into tha DB via a DBMS pgAdmin4). Then in the start of every month 01.mm.yyyy the crawler is activated, the data is wrangled and new data is fed to the DB. Finally, the full data is loaded into a dataframe and returned.

## Monthly scraping (Crawler)

The crawler scrapes data from the last month until start of the current one. It saves the last crawled date into another Table in the DB, that specifically salves the dates. That way the dates can be accessed for the next month. It goes to IDAWEB, navigates through the website, makes the order, which is then unzipped into txt files and saved locally and temporarily.

## Wrangler

The data in the locally stored txt files are imported and wrangled. Then it is saved in one dataframe. To avoid storing unnecessary data over time, the txt files are deleted after extracting the data.
