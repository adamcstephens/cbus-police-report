#!/usr/bin/env python

import argparse
import requests
import smtplib
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dns.resolver
import sys

yesterday = date.today() - timedelta(1)
daybefore = date.today() - timedelta(2)
todate = yesterday.strftime("%m/%d/%Y")
fromdate = daybefore.strftime("%m/%d/%Y")

def get_mx_host(email):
    domain = str.split(email, '@')[1]
    answers = dns.resolver.query(domain, 'MX')
    # return first MX host
    return str(answers[0].exchange)[:-1]


def get_police_report(district,incident_types='9'):
    r = requests.get('http://www.columbuspolice.org/reports/Results?from=%s&to=%s&loc=%s&types=%s' % (fromdate, todate, district, incident_types))
    # return full html page
    return r.text

def send_email(fromemail, toemail, htmlcontent):
    if args.usemx:
        mailserver = get_mx_host(toemail)
    else:
        mailserver = args.mailserver

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Local Police Reports: %s - %s" % (fromdate, todate)
    msg['From'] = fromemail
    msg['To'] = toemail

    textcontent = 'No text content'
    part1 = MIMEText(textcontent, 'plain')
    part2 = MIMEText(htmlcontent, 'html')
    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP(mailserver)
    s.sendmail(fromemail, toemail, msg.as_string())
    s.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Columbus Police Daily Report')
    parser.add_argument('fromemail')
    parser.add_argument('toemail')
    parser.add_argument('--district', default='all', help='District to use (defaults to all)')
    parser.add_argument('--usemx', help='Use MX records', action='store_true')
    parser.add_argument('--mailserver', help='Mail server to use')
    args = parser.parse_args()

    if not args.mailserver and not args.usemx:
        print("Must pass a mailserver or usemx")

    emailcontent = get_police_report(args.district)
    send_email(args.fromemail, args.toemail, emailcontent)
