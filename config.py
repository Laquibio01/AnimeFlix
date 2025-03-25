# config.py
import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='tu_host',
        user='tu_usuario',
        password='tu_contraseña',
        database='tu_base_de_datos'
    )
    return connection
