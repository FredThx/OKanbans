#!/usr/bin/env python
# -*- coding:utf-8 -*

'''Pour communiquer avec NiceLabel
'''


import requests
from keyword import iskeyword
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('chardet.charsetprober').setLevel(logging.WARNING)

class NiceLabel:
    pass

class HttpNiceLabel(NiceLabel):
    ''' Pour communiquer en http avec NiceLabel
    '''

    def __init__(self, url = 'http://127.0.0.1:56425', timeout = 5):
        '''Initialisation
            url        :   ex 'http://127.0.0.1:56425'
            timeout    :   default 5 secondes
        '''
        self.url = url
        self.timeout = timeout

    def print(self, **params):
        '''Print label(s)
            **params    all the variables
        '''
        #Pour utiliser les script python dans NiceLabel :
        # il faut que les noms de champs soient des noms de variables python valides...
        params2 = {}
        for param in params:
            val = params[param]
            if isinstance(val,str):
                val = val.rstrip()
            params2[self.valide_name(param)]=val

        #print(params2)
        r=requests.get(self.url, params=params2, timeout = self.timeout)
        logging.debug(f"Request : {r.url}")
        return r.text

    def valide_name(self, var_name):
        '''tranforme un nom en nom de variable valide
        C'est à dire :
            - les '.' sont remplacés par des '_'
            - si le nom commence par un chiffre, on ajout '_' devant
            - si le nom est un mot clef (ex : 'from'), on ajout '_' devant
        '''
        var_name = var_name.replace('.','_')
        if iskeyword(var_name) or not var_name.isidentifier():
            var_name = "_" + var_name
        return var_name

    def status(self):
        '''Renvoie True si le serveur Nicelabel répond
        '''
        try:
            r=requests.get(self.url+"/?mode=test", timeout = self.timeout)
            if r.text == "Ok":
                return True
            else:
                return False
        except :
            return False
