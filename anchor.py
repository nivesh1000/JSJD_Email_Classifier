raw_body = '''<div style="background:#FFFFFF; color:#666666; font-family:Arial,Helvetica,sans-serif; font-size:12px; line-height:18px" align="center">You are subscribed to this email as txoga@associationrevenuepartners.com.<br>Click here to modify your <a style="color:#666666; text-decoration:underline" data-auth="NotApplicable" rel="noopener noreferrer" target="_blank" href="http://click.arpnewsletters.com/form?2wp5qj--158ad-kx0pihm8&amp;sl=4jg&amp;t=1&amp;ac=gpgp" title="http://click.arpnewsletters.com/form?2wp5qj--158ad-kx0pihm8&amp;sl=4jg&amp;t=1&amp;ac=gpgp" data-linkindex="80" id="anchor-5e27cd04-1027-22e9-0d8b-874b5e5b392a">preferences</a> or <a style="color:#666666; text-decoration:underline" data-auth="NotApplicable" rel="noopener noreferrer" target="_blank" href="http://click.arpnewsletters.com/form?2wp5qj--158ad-kx0pihm8&amp;sl=4jg&amp;t=5&amp;ac=gpgp" title="http://click.arpnewsletters.com/form?2wp5qj--158ad-kx0pihm8&amp;sl=4jg&amp;t=5&amp;ac=gpgp" data-linkindex="81">unsubscribe</a>.</div>'''
from bs4 import BeautifulSoup

body = (
    BeautifulSoup(
        raw_body, "html.parser")
)

for a_tag in body.find_all("a"):
    a_tag.decompose()

# Extract cleaned text
space_free_body = body.get_text().strip().replace("\u200c", "").replace("\xa0", "").replace("\n", "").replace("\r", "")
print(space_free_body)