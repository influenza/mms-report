# mms-report

This utility is to create an easily shareable HTML view of the
contents of the mms database from an Android device.

This utility makes a lot of assumptions and will not work for all
versions of the Android operating system or messaging utilities.

# Installation

### Dependencies

[Jinja2](http://jinja.pocoo.org/docs/dev/intro/) is used as a templating
engine. You'll need to install if it isn't available on your system yet.

### Virtual environment setup

    $ git clone this-repo
    $ cd this-repo/
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

# Notes on the database format

I didn't read any spec on the format of the mmssms.db database. Instead
I just looked at the tables and tried to make sense of it. I use the sms
table for most of the content.

If `sms.type = 1` then the message was received from `sms.address`. If
`sms.type = 2` then the message was sent to `sms.address`.

For mms messages, if `pdu.m_type = 132` then the message was received. If
`pdu.m_type = 128` then the message was sent.

Dates are stored as milliseconds since the epoch.
