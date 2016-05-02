import itertools
import jinja2
import sqlite3

from string import Template
from datetime import datetime

jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('mmsreport', 'templates'))
conversation_template = jinja_env.get_template('conversation.html')

def conversations_report(input_file, contacts):
    """
    Connect to the SQLite db at input_file and generate a report per conversation
    """
    conn = sqlite3.connect(input_file)
    c = conn.cursor()
    sms_query = '''
    SELECT
        ca.address number,
        sms.thread_id thread,
        sms.date / 1000 date,
        CASE WHEN sms.type = 1 THEN 't' ELSE 'f' END received,
        'f' has_attachment,
        sms.body text

    FROM sms INNER JOIN threads ON sms.thread_id = threads._id
        INNER JOIN canonical_addresses ca ON CAST(ca._id AS TEXT) = threads.recipient_ids
        ORDER BY sms.thread_id, sms.date
    '''
    query = c.execute(sms_query)
    column_names = [ i[0] for i in query.description ]
    sms_messages = [ dict(zip(column_names, row)) for row in query.fetchall() ]

    mms_query = '''
    SELECT
        ca.address number,
        pdu.thread_id thread,
        pdu.date date,
        CASE WHEN pdu.m_type = 132 THEN 't' ELSE 'f' END received,
        't' has_attachment,
        part.text text

    FROM pdu INNER JOIN threads ON pdu.thread_id = threads._id
        INNER JOIN part ON part.mid = pdu._id
        INNER JOIN canonical_addresses ca ON CAST(ca._id AS TEXT) = threads.recipient_ids
        WHERE part.ct = 'text/plain'
        ORDER BY pdu.thread_id, pdu.date
    '''
    query = c.execute(mms_query)
    column_names = [ i[0] for i in query.description ]
    mms_messages = [ dict(zip(column_names, row)) for row in query.fetchall() ]

    message_corpus = sorted(sms_messages + mms_messages,key = lambda x: (x['thread'], x['date']))

    def row_to_template_msg(row):
        attachment = '   ' if row['has_attachment'] == 'f' else '(*)'
        sender = "Me" if row['received'] == 'f' else contacts.get(row['number'], row['number'])
        date_string = datetime.fromtimestamp(row['date']).strftime('%Y-%m-%d %H:%M:%S')
        message_text = row['text']
        return {
                'has_attachment' : attachment,
                'sent' : row['received'] == 'f',
                'sender' : sender,
                'date' : date_string,
                'message_text' : message_text
        }

    for thread, messages in itertools.groupby(message_corpus, key = lambda x: x['thread']):
        messages_for_template = list(map(row_to_template_msg, messages))
        start_date = messages_for_template[0]['date']
        end_date = messages_for_template[-1]['date']

        html_text = conversation_template.render(
                messages=messages_for_template,
                start_date=start_date, end_date=end_date,
                thread=thread)
        with open("thread-{0}.html".format(thread), 'w') as f:
            f.write(html_text)
