import datetime
import logging
import json
import requests
import re
import lxml.etree as ET
import urllib.request

import azure.functions as func


def main(mytimer: func.TimerRequest, inputblob: func.InputStream) -> func.HttpResponse:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    xslt = inputblob.read()
    logging.info(f"Blob conetnt: {inputblob.read()}")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    
    input = requests.get('https://book.stadeiga.com/courtbooking/home/calendarDayView.do?id=29')
    
    url = 'https://book.stadeiga.com/courtbooking/home/calendarDayView.do?id=29'
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    respData = resp.read().decode('utf-8', "ignore")
    
    #logging.info(respData)
    
    content_withoutscript = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>' , r'', respData, flags=re.M)
    content_withoutstyle = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>' , r'', content_withoutscript, flags=re.M)
    content_withouthref = re.sub(r'href=\".*?\"' , r'', content_withoutstyle, flags=re.M)
    content_withoutemptyline = re.sub(r'^(?:[\t ]*(?:\r?\n|\r))+', r'', content_withouthref, flags=re.M)
    content_withoutfooter = re.sub(r'(<div id=\"footer\">(.|\n)*)<\/td>',r'</td>' , content_withoutemptyline, flags=re.M)
    content_withoutdiv = re.sub(r'(<div id=\"debuglog\">(.|\n|<\/div>)*)<\/div>', r'' , content_withoutfooter, flags=re.M)
    content_withoutdoc = re.sub(r'(<!DOCTYPE(.)*\">)', r'' , content_withoutdiv, flags=re.M)
    content_withoutdoc = content_withoutdoc.replace("<html xmlns=\"http://www.w3.org/1999/xhtml\"", "<data").replace("</html", "</data").replace("DIV","div").replace("undefined","").replace("&nbsp;","").replace(" align=center","").replace("<a class=\"calheaderdaylink\" />","<a class=\"calheaderdaylink\" >").replace("\'border\'","\"border\"").replace("\r","").replace("\n","").replace("\t","").replace("<Style>","<style>")
    
    
    #logging.info(content_withoutdiv)
    
    dom = ET.fromstring(content_withoutdoc)
    xslt = ET.fromstring(xslt)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    prettynewdom =ET.tostring(newdom)
    
    #logging.info(prettynewdom.decode("utf-8") )
    
    data = {}
    data['body'] = prettynewdom.decode("utf-8") 
    json_data = json.dumps(data)
    
    logging.info(json_data)
    r = requests.post('https://prod-04.northcentralus.logic.azure.com:443/workflows/c5c1e8f1449d40d6b5ca93e2aafe7111/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=antZQwk1ffWWBr_k-sRKkA7f7EYwab2aD42tf-K3EaY', json=json_data)
    print(r.status_code, r.reason)
    