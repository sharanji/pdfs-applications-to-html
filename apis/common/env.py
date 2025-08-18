# MQSQL_CONNECTION_STRING = "mysql+pymysql://avnadmin:AVNS_qAgkXwcrZoWvmQETwn3@mysql-3616c618-sharanji-b576.l.aivencloud.com:10450/defaultdb"
# MQSQL_CONNECTION_STRING = "mysql+pymysql://root:rootroot@localhost:3306/xcahnge"
MQSQL_CONNECTION_STRING = "mysql+pymysql://avnadmin:AVNS_qAgkXwcrZoWvmQETwn3@mysql-3616c618-sharanji-b576.l.aivencloud.com:10450/defaultdb"

def is_production():
    return False

def is_staging():
    return True