from flask_sqlalchemy import SQLAlchemy
import pymysql
import random, re


database = SQLAlchemy()

MYSQLUSER = 'root'
MYSQLDB = 'bugdb'
PASSWORD = ''


def connect_db():
    conn = pymysql.connect(host='localhost', user=MYSQLUSER, passwd=PASSWORD, db=MYSQLDB)
    return conn


def runSql(query, conn):
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# The debug procedures

def m_debug(conn, text):
    query = """insert into m_debug (text) values ('"""+text+"""');"""
    result = runSql(query, conn)
    conn.commit()


def getDebug(conn):
    query = """select text from m_debug;"""
    result = runSql(query, conn)
    debug_log = [row[0] for row in result]
    return debug_log


def flushDebug(conn):
    query = """delete from m_debug;"""
    result = runSql(query, conn)


# Now the application procedures.

def getBugList(conn, user):
    query = """
    SELECT bh.bug_id, bh.bug_title, u.username, bh.priority, bh.customer, bh.status
    FROM bug_header bh, users u
    WHERE u.id = bh.assigned_to_user_id AND u.username = '%s'
    ORDER by bh.priority, bh.bug_id, bh.status;
    """ % user
    result = runSql(query, conn)
    bugList = [dict(bug_id=row[0], title=row[1], assigned_to=row[2], priority=row[3], customer=row[4], status=row[5]) for row in result]
    return bugList


def create_user(conn, email, password):
    """
    This adds a new user from the email_id
    """
    username = re.split('@', email)[0]
    # username = email_id.replace('@iese.edu', '')
    query = """
    INSERT INTO users (id, password, username, status)
    VALUES ('%s', md5('%s'), '%s', 'A');
    """ % (email, password, username)

    # TODO: check success
    result = runSql(query, conn)

    return True

    
def getUser(conn, username):
    """ This will return the user dictionary"""
    m_debug(conn, 'Entering getUser to get user details for the username: %s ' % username)

    query = """select u.id, u.username, u.status, u.email FROM users u WHERE u.username = '%s';""" % username
    
    result = runSql(query, conn)
    
    if len(result) > 0:
        entries = [dict(user_id=row[0], username=row[1], status=row[2], email=row[3]) for row in result]
        entries = entries[0]
        m_debug(conn, 'Entry found in getUser for the username :'+entries['username'])
    else:
        entries = False
        
    return entries


def getUserID(conn, user_id):
    """ This will return the user dictionary"""
    
    query = """select u.id, u.user_first_name, u.user_last_name, u.cost, u.status,u.email_id,c.company_id, c.company_name, c.default_currency as currency from users u, company c where u.user_id = '"""+user_id+"""' and u.company_id = c.company_id"""
    
    result = runSql(query, conn)
    
    if len(result) > 0:
        entries = [dict(user_id = row[0], user_first_name=row[1], user_last_name=row[2], email_id=row[5], company_id=row[6], cost=row[3], company_name=row[7]) for row in result]
    else:
        entries = False
        
    return entries


# for bugs

def createBug(conn, title, description, username, priority, customer):
    m_debug(conn, 'Inside db.createBug')
    user = getUser(username)
    user_id = user['user_id']
    query = """insert into bug_header (bug_title, bug_description, assigned_to_user_id, priority, customer) values ( '"""+title+"""','"""+description+"""',str("""+user_id+"""),str("""+priority+"""), '"""+customer+"""');"""
    result =runSql(query,conn)

 
def createBug2(conn, bug):
    user_id = str(bug['user_id'])
    m_debug(conn, str(user_id))
    query = """insert into bug_header ( bug_title, bug_description, assigned_to_user_id, priority, customer, status) values ( '"""+bug['title']+"""','"""+bug['description']+"""',"""+user_id+""","""+bug['priority']+""", '"""+bug['customer']+"""','OPEN');"""
    result =runSql(query,conn)


def getBugHeader(conn, bug_id):
    query = """
    SELECT b.bug_id, b.bug_title, b.bug_description, b.assigned_to_user_id, b.customer,
    b.status, u.username, b.priority
    FROM bug_header b, users u
    WHERE b.assigned_to_user_id = u.id AND bug_id = %s;
    """ % bug_id
    r = runSql(query, conn)[0]
    bugh = dict(bug_id=r[0], title=r[1], description=r[2], assigned_to_user_id=r[3], customer=r[4], status=r[5], assigned_to_username=r[6], priority=r[7])
    return bugh


def getBugBody(conn, bug_id):
    query = """
    SELECT b.bug_update, b.last_updated_time, b.updated_by, u.username
    FROM bug_body b, users u
    WHERE u.id = b.updated_by AND b.bug_id = %s
    ORDER by last_updated_time;""" % bug_id
    result = runSql(query, conn)
    bugb = [dict(update=row[0], updated_by=row[1], updated_by_username=row[3]) for row in result]
    return bugb


def updateBugHeader(conn, bug):

    query = """update bug_header set bug_title = '"""+bug['title']+ \
        """', bug_description = '"""+bug['description']+ \
        """', assigned_to_user_id = """+str(bug['assigned_to_user_id'])+""", customer = '""" \
        + bug['customer']+"""', status = '"""+bug['status']+ \
        """', priority = """+str(bug['priority'])+""" where bug_id = """+ str(bug['bug_id'])

    result = runSql(query, conn)
    

def insertBugUpdate(conn, bug):

    bug['update'] = bug['update'].replace("'","\\'")
    
    query = """ insert into bug_body (bug_id, bug_update, updated_by) values ("""+str(bug['bug_id'])+""", '"""+bug['update']+"""', """+str(bug['updated_by_user_id'])+""");"""

    result = runSql(query, conn)
    

def getUserName(conn, user_id):

    query = """select username from users where id = """+str(user_id)
    result = runSql(query,conn)[0]

    return result


def getUsers(conn):

    query = """select username,id from users where status = 'A';"""
    result = runSql(query, conn)

    users = [dict(user_id=row[1], username=row[0]) for row in result]
    
    return users


def getAllQueues(conn):
    all_users = getUsers(conn)
    all_queues = []
    for user in all_users:
        queue = getBugList(conn, user['username'])
        summary = dict(username=user['username'], queue=queue)
        all_queues.append(summary)
    return all_queues


def getCategories(conn):
    query = """select 
        c1.category_id,
        c1.category_name,
        c1.category_description,
        c1.parent_category_id,
        c1.category_owner_id,
        c2.category_name as parent_Category_name,
        c2.category_description as parent_category_description,
        u.user_name,
        u.email_id
    from
        categories c1, categories c2, users u
    where
        c1.parent_category_id = c2.category_id and c1.category_owner_id = u.user_id
    """

    result = runSql(query, conn)
    cats = [dict(category_id=row[0], category_name=row[1], category_description = row[2], parent_category_id = row[3], category_owner_id = row[4], parent_category_name = row[5], parent_category_description = row[6], owner_username = row[7], owner_email_id = row[8]) for row in result]

    return cats
