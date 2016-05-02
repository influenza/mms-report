from mmsreport.reports import conversations_report

if __name__ == '__main__':
    import argparse

    input_file = './data.db'
    # optional contact list
    contacts = {
        # Use 'Canonical' number format here
        '(888) 555-1212': 'Fake Number',
    }
    conversations_report(input_file, contacts)
