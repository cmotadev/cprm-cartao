import os
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))

# SQLAlchemy
# SQLALCHEMY_DATABASE_URI = "sqlite:///app.sqlite3"
SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=' + quote_plus('DRIVER=FreeTDS;SERVER=10.19.2.66;PORT=1433;'
                                                                        'DATABASE=totvs_cprm;UID=cartao_visita;'
                                                                        'PWD=apresentacao;TDS_Version=7.3;')
