import psycopg2
import os

def read_connection_config(filename):
    config = {}
    filepath = os.path.abspath(filename)
    with open(filepath, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config
    
def postgres_conn(filename):
    config = read_connection_config(filename)
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    return conn, cursor
