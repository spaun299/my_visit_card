import os


def get_db_url():
    return "dbname='me' user='postgres' host='localhost' password='7847473'" \
        if not os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL') \
        else "dbname='me' user='{user_name}' host='{host}' " \
             "port='{port}' password='{password}'".format(
            user_name=os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'],
            host=os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
            port=os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],
            password=os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'])

DEBUG = False
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
