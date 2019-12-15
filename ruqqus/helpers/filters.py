import yaml
from bs4 import BeautifulSoup
from flask import *
from os import environ
from urllib.parse import urlparse
from ruqqus.classes import Domain
from ruqqus.__main__ import db, app

def filter_comment_html(html_text):

    
    soup = BeautifulSoup(html_text)

    links = soup.find_all("a")

    domain_list=set()

    for link in links:

        domain=urlparse(link["href"]).netloc

        #parse domain into all possible subdomains
        parts=domain.split(".")
        for i in range(len(parts)):
            new_domain=parts[i]
            for j in range(i+1, len(parts)):
                new_domain+="."+parts[j]

                domain_list.add(new_domain)
        

    #search db for domain rules that prohibit commenting
    bans=[x for x in db.query(Domain).filter_by(can_comment=False).filter(Domain.domain.in_(list(domain_list))).all()]

    if bans:
        return bans
    else:
        return []
