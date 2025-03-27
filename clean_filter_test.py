from bs4 import BeautifulSoup
from unidecode import unidecode
import unittest
from filter import classify_emails
from get_filters import fetch_groups
import re   

filters_and_deletion_emails = fetch_groups()
filters= filters_and_deletion_emails["data"]["groups"]
for filter in filters:
    print(filter)

def text_normalize(text):
    return re.sub(r'\s+', ' ', text)


def html_seperator(html,seperator):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    # Get the <body> tag; return empty string if none exists
    body = soup.body

    if not body:
        return ""
    text = body.get_text(seperator)


    normalized_text = text_normalize(unidecode(text).strip())

    
    return normalized_text



def use_filter(object,seperator=' '):



    object[0]["body"]=html_seperator(object[0].get("body"),seperator)
    # print(repr(object[0]["body"]))
    return classify_emails(object,filters)[0]["group"]


group=use_filter([{
    "subject": "Hello",
    "body": '''
 <html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style type="text/css" style="display:none">
<!--
p
        {margin-top:0;
        margin-bottom:0}
-->
</style></head><body dir="ltr"><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><b>Dear [User],</b></div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">We’ve received your request to stop receiving communications from us.</div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">You indicated that you either <b>didn't subscribe</b>&nbsp;to our emails, or you no longer wish to be contacted.</div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">Please find the actions you can take below:</div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">🔹 <b>Cease all future emails:</b><br>✅ <b>Do Not Contact – Unsubscribe &amp; Block Emails</b></div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">🔹 <b>Permanently delete your account and personal data:</b><br>✅ <b>Delete Me – Erase My Data</b></div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">Once actioned, you will receive <b>no further contact</b>&nbsp;from us.</div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">If you made this request by mistake, or wish to subscribe again, you can do so anytime from our website.</div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">For assistance, please contact:<br>📩 <b>Support Team</b><br>☎️ <b>Customer Care</b></div><div class="elementToProof" style="margin-top:1em; margin-bottom:1em; font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><b>The [Company Name] Data Privacy Office</b></div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><br></div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><br></div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><br></div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><br></div><div id="Signature" class="elementToProof"><p style="text-align:left; background-color:rgb(255,255,255); margin:0px; font-family:Calibri,Arial,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)"><span style="font-size:10pt; color:rgb(68,114,196)"><b>Thanks &amp; Regards</b></span></p><p style="margin:0in; font-size:11pt"><span style="font-family:Calibri,Arial,Helvetica,sans-serif; font-size:10pt; color:rgb(68,114,196)"><b>Jaichand Verma | QA&nbsp;Consultant&nbsp;</b></span></p><p style="text-align:left; background-color:white; margin:0in; font-family:Calibri,sans-serif; font-size:11pt; color:rgb(36,36,36)"><span style="font-size:14pt; color:black"><sup><img width="18" height="18" data-outlook-trace="F:1|T:1" src="cid:ab4da7b4-e569-4fa8-99ab-06c9d29a2ef2" style="width:0.1979in; height:0.1979in; min-width:auto; min-height:auto; margin:0px"></sup></span><span style="font-family:Arial,sans-serif; font-size:14pt; color:rgb(102,102,102)"><sup>&nbsp; </sup></span><span style="font-size:14pt; color:rgb(102,102,102); background-color:white"><b><sup>US</sup></b><sup>&nbsp;+1-415-429-6641,&nbsp; </sup><b><sup>UAE</sup></b><sup>&nbsp;+9714-313-2517, </sup><b><sup>India</sup></b><sup>&nbsp;+91-135-260-8366</sup></span></p><p style="text-align:left; background-color:white; margin:0in; font-family:Calibri,sans-serif; font-size:11pt; color:rgb(36,36,36)"><span style="color:black"><img width="20" height="20" data-outlook-trace="F:1|T:1" src="cid:3f7021ab-9c0d-4d12-9c80-38c4bc4c505e" style="width:0.2187in; height:0.2187in; min-width:auto; min-height:auto; margin:0px"></span><span style="font-size:12pt; color:rgb(102,102,102)">&nbsp; </span><span style="font-size:14pt; color:rgb(102,102,102)"><sup>Microsoft Solutions Partner |&nbsp;Salesforce Consulting Partner</sup></span></p><p style="text-align:left; background-color:white; margin:0in; font-family:Calibri,sans-serif; font-size:11pt; color:rgb(36,36,36)"><span style="color:black"><img width="16" height="16" data-outlook-trace="F:1|T:1" src="cid:0252b865-ce3b-44c2-884d-455637d9c095" style="width:0.177in; height:0.177in; min-width:auto; min-height:auto; margin:0px"></span><span style="font-size:12pt; color:black">&nbsp; </span><span style="font-size:14pt; color:blue"><b><sup><u><a href="http://www.cynoteck.com/" target="_blank" class="ContentPasted5" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="5" style="color:blue; margin:0px">www.cynoteck.com</a></u></sup></b></span><span style="font-family:Arial,sans-serif; font-size:14pt; color:rgb(102,102,102)"><b><sup>&nbsp;| </sup></b></span><span style="font-size:14pt; color:blue"><sup><u><a href="https://www.linkedin.com/company/cynoteck-technology-solutions-private-limited" target="_blank" class="ContentPasted5" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="6" style="color:blue; margin:0px">LinkedIn</a></u></sup></span><span style="font-size:14pt; color:black"><sup>&nbsp;| </sup></span><span style="font-size:14pt; color:blue"><sup><u><a href="https://clutch.co/profile/cynoteck-technology-solutions#summary" target="_blank" class="ContentPasted5" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="7" style="color:blue; margin:0px">Clutch</a></u></sup></span><span style="font-size:14pt; color:black"><sup>&nbsp;| </sup></span><span style="font-size:14pt; color:blue"><sup><u><a href="https://cynoteck.com/blog-post/" target="_blank" class="ContentPasted5" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="8" style="color:blue; margin:0px">Blog</a></u></sup></span></p></div></body></html>
    '''
     }]," ")
print(group)

# class TestExtractTextWithBreaks(unittest.TestCase):

#     def test_with_para_tag(self):
#         object=[{
#         "subject": "Hello",
#         "body": '''
#             <body>
#                 <p><b>test</b> p</p>
#                 <div>out of office</div>
#             </body>
#         '''
#          }]
#         result = use_filter(object," ")
#         expected = [{'group_id': 10, 'keyword_id': [57]}, {'group_id': 11, 'keyword_id': [67]}]
#         self.assertEqual(result, expected)

#     def test_with_bold(self):
#         object=[{
#         "subject": "Hello",
#         "body": '''
#             <body>
#                 <p>test p</p>
#                 <div>out <b>of</b>  office</div>
#             </body>
#         '''
#          }]
#         result = use_filter(object," ")
#         expected = [{'group_id': 11, 'keyword_id': [67]}]
#         self.assertEqual(result, expected)        

#     def test_with_seperate_div(self):
#         object=[{
#         "subject": "Hello",
#         "body": '''
#             <body>

#                 <div>test div</div>
#                 <span>out of office</span>                
#                 <div></div>
#             </body>
#         '''
#          }]
#         result = use_filter(object," ")
#         expected = [{'group_id': 10, 'keyword_id': [57]}, {'group_id': 11, 'keyword_id': [67]}]
#         self.assertEqual(result, expected)        




# if __name__ == '__main__':
#     unittest.main()        
