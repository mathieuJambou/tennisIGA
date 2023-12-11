##from dataclasses import replace
import re
import lxml.etree as ET

with open ('payloadtennis.html', 'r') as f:
    content = f.read()
    content_withoutscript = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>' , r'', content, flags=re.M)
    content_withoutstyle = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>' , r'', content_withoutscript, flags=re.M)
    content_withouthref = re.sub(r'href=\".*?\"' , r'', content_withoutstyle, flags=re.M)
    content_withoutemptyline = re.sub(r'^(?:[\t ]*(?:\r?\n|\r))+', r'', content_withouthref, flags=re.M)
    content_withoutfooter = re.sub(r'(<div id=\"footer\">(.|\n)*)<\/td>',r'</td>' , content_withoutemptyline, flags=re.M)
    content_withoutdiv = re.sub(r'(<div id=\"debuglog\">(.|\n|<\/div>)*)<\/div>', r'' , content_withoutfooter, flags=re.M)
    
    content_withoutdiv = content_withoutdiv.replace("<html xmlns=\"http://www.w3.org/1999/xhtml\"", "<data").replace("</html", "</data").replace("DIV","div").replace("undefined","").replace("&nbsp;","").replace(" align=center","").replace("<a class=\"calheaderdaylink\" />","<a class=\"calheaderdaylink\" >")
    
    print(content_withoutdiv)
    file = open("output.xml", "w")
    file.write(content_withoutdiv)
    file.close
    
    dom = ET.parse('output.xml')
    xslt = ET.parse('tennis.xsl')
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    prettynewdom =ET.tostring(newdom, pretty_print=True)
    open('result.xml', 'wb').write(prettynewdom)

    

    
    