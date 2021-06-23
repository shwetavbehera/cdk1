# Challenge Klimadaten 2021
This is the repository for Challenge Klimadaten.

We created a web dashboard to display snow data from Graubunden ski locations.

The dashboard is created in **Dash**, for visualization we use **Plotly**, we scrape data using the **requests** and 
**BeautifulSoup4** libraries.

## Needed libraries

You need to install the following libraries:

- dash
- pandas
- requests
- BeautifulSoap4
- plotly
- os
- psycopg2
- datetime 
- sys
- time 
- requests
- re
- zipfile
- glob
- io


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
