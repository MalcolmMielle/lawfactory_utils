import re
from urllib.parse import urljoin, parse_qs, urlparse, urlunparse

def pre_clean_url(url):
    if url.startswith('www'):
        url = "http://" + url
    if url.startswith('/leg/http'):
        url = url[5:]
    return url

re_clean_ending_digits = re.compile(r"(\d+\.asp)[\dl]+$")
def clean_url(url):
    url = url.strip()

    # fix urls like 'pjl09-518.htmlhttp://www.assemblee-nationale.fr/13/ta/ta0518.asp'
    if url.find('https://') > 0:
        url = 'https://' + url.split('https://')[1]
    if url.find('http://') > 0:
        url = 'http://' + url.split('http://')[1]

    # fix url like http://www.senat.fr/dossier-legislatif/www.conseil-constitutionnel.fr/decision/2012/2012646dc.htm
    if 'www.conseil-' in url:
        url = 'http://www.conseil-' + url.split('www.conseil-')[1]

    scheme, netloc, path, params, query, fragment = urlparse(url)

    path = path.replace('//', '/')

    if 'legifrance.gouv.fr' in url:
        params = ''
        url_jo_params = parse_qs(query)
        if 'cidTexte' in url_jo_params:
            query = 'cidTexte=' + url_jo_params['cidTexte'][0]

        if netloc == 'legifrance.gouv.fr':
            netloc = 'www.legifrance.gouv.fr'
        if 'jo_pdf.do' in path and 'id' in url_jo_params:
            path = 'affichTexte.do'
            query = 'cidTexte=' + url_jo_params['id'][0]

        path = path.replace('./affichTexte.do', 'affichTexte.do')

    if 'senat.fr' in netloc:
        path = path.replace('leg/../', '/')
        path = path.replace('dossierleg/', 'dossier-legislatif/')

    if netloc == 'webdim':
        netloc = 'www.assemblee-nationale.fr'

    # force https
    if 'assemblee-nationale.fr' not in netloc and 'conseil-constitutionnel.fr' not in netloc:
        scheme = 'https'

    # url like http://www.assemblee-nationale.fr/13/projets/pl2727.asp2727
    if 'assemblee-nationale.fr' in url:
        path = re_clean_ending_digits.sub(r"\1", path)

    return urlunparse((scheme, netloc, path, params, query, fragment))

