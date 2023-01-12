#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Projet : montage
silvercs.py :

class SilverCS : une base de données progress Silver CS accéssible via ODBC


'''
import time, datetime
import requests
import json
try:
    import pyodbc
except:
    pass
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('chardet.charsetprober').setLevel(logging.WARNING)

class SilverCS:
    '''Une base de données Silver CS
    '''

    def __init__(self, json_format_suivi = "format_suivi.json"):
        '''Initialisation
            - json_format_suivi      :   un fichier json qui décrit le formatage du fichier de suivit à envoyer à SilverCS
        '''
        self.json_format_suivi = json_format_suivi

    def select_one(self, champs, xfrom, where = None, alias = None):
        '''Execute une requête SELECT et retourne un dict
            champs  :   list de nom de champs (ex : ['stecod', 'ofnum'])
            xfrom   :   clause FROM (ex : "PUB.SFOA")
            where   :   (facultatif) clause WHERE (ex : "noof = '42'")
            alias   :   (facultatif mais si present, doit modifier tous les champs) liste des des nom de champs du dict de sortie (ex : ['Code_societe', 'no_of'])
        '''
        req = "SELECT %s FROM %s"%(",".join(champs), xfrom)
        if where:
            req += " WHERE "+ where
        result = self.fetchone(req)
        if alias is None:
            return dict(zip(champs, result))
        else:
            return dict(zip(alias, result))
    def __str__(self):
        return "SilverCS"

    def select_all_old(self, champs, xfrom, where = None, alias = None):
        '''Execute une requête SELECT et retourne une liste de dict
            champs  :   list de nom de champs (ex : ['stecod', 'ofnum'])
            xfrom   :   clause FROM (ex : "PUB.SFOA")
            where   :   clause WHERE (ex : "noof = '42'")
            alias   :   (facultatif mais si present, doit modifier tous les champs) liste des des nom de champs du dict de sortie (ex : ['Code_societe', 'no_of'])
        '''
        req = "SELECT %s FROM %s"%(",".join(champs), xfrom)
        if where:
            req += " WHERE "+ where
        results = self.fetchall(req)
        if alias is None:
            return [dict(zip(champs, result)) for result in results]
        else:
            return [dict(zip(alias, result)) for result in results]

    def select_all(self, req):
        '''Execute une requête SELECT et retourne une liste de dict
        '''
        return self.fetchall(req)


    def get_of_datas(self, noof, langues = ['AN', 'AL']):
        '''Renvoie toutes les données liées au noof
        sous la forme d'un dict{'champ1' : val1, ...}
        '''
        now = time.time()
        #DONNEES ISSUES DE l OF
        results = self.select_one( \
            ['PUB.SOFA.ofnum', 'PUB.SOFD.openum', 'PUB.SOFA.oftype','PUB.SOFA.ofetat', 'PUB.SOFA.ofstatut','PUB.SOFA.ofref', \
            'PUB.SOFB.proref', 'PUB.SOFB.ofbqteini','PUB.SOFB.ofbqterea', 'PUB.SOFB.clicod', 'PUB.SOFB.etsnum', 'PUB.SOFB.cdenum'], \
            '(PUB.SOFA INNER JOIN PUB.SOFB ON PUB.SOFA.ofanumenr = PUB.SOFB.ofanumenr) INNER JOIN PUB.SOFD ON PUB.SOFA.ofanumenr = PUB.SOFD.ofanumenr', \
            "PUB.SOFA.stecod = '07' and PUB.SOFA.ofnum = '%s' and PUB.SOFD.opesuiqte='1'"%noof)
        if 'PUB.SOFB.proref' in results:
            results.update(self.get_proref_datas(results['PUB.SOFB.proref'], langues))
            #DONNEES CLIENT
            if results['PUB.SOFB.clicod']:
                results.update(self.select_one( \
                ['PUB.SDTCLE.adrnom','PUB.SDTCLE.adrbdi'], \
                "PUB.SDTCLE", \
                "PUB.SDTCLE.clicod = '%s' AND PUB.SDTCLE.etsnum = '%s'"%(results['PUB.SOFB.clicod'],results['PUB.SOFB.etsnum'])))
        else:
            results = {}
        logging.debug("Durée d'extraction des données : %s secondes"%(time.time()-now))
        logging.debug(results)
        return results

    def get_proref_datas(self, proref, langues = ['AN', 'AL'], clicod = None):
        '''Renvoie toutes les données liées a un produit
        sous la forme d'un dict{'champ1' : val1, ...}
        '''
        #DONNEES ISSUES DU PRODUIT
        results=self.select_one( \
            ['PUB.SDTPRA.prodes1', 'PUB.SDTPRA.prodes2','PUB.SDTPRA.promotdir', \
            'PUB.SDTPRB.gencod', 'PUB.SDTPRC.propdsuni', \
            'PUB.SDTPRC.prdetqcod','PUB.SDTPRC.prdetqcod2','PUB.SDTPRC.prdembqte', 'PUB.SDTPRC.prdembpds', 'PUB.SDTPRC.prdembqte2'], \
            "(PUB.SDTPRA INNER JOIN PUB.SDTPRB ON PUB.SDTPRA.pronumenr = PUB.SDTPRB.pronumenr) INNER JOIN PUB.SDTPRC ON PUB.SDTPRB.varnumenr = PUB.SDTPRC.varnumenr", \
            "PUB.SDTPRA.proref = '%s'"%proref)
        #DESIGNATIONS ETRANGERES
        for langue in langues:
            results.update(self.select_one( \
                ['PUB.SPALIB.liblan', 'PUB.SPALIB.liblan2'], \
                'PUB.SDTPRA INNER JOIN PUB.SPALIB ON PUB.SDTPRA.libnum = PUB.SPALIB.libnum', \
                "PUB.SDTPRA.proref='%s' AND PUB.SPALIB.lancod = '%s'"%(proref,langue), \
                alias = ["prodes1_%s"%langue, "prodes2_%s"%langue]))
        #ZONES PARAMETRABLES PRODUITS
        for zpa in self.select_all( \
            ['PUB.SDTZPA.zpacod', 'PUB.SPAZPA.zpatyp', 'PUB.SDTZPA.zpaval', 'PUB.SDTZPA.zpavalnum'], \
            '(PUB.SDTPRA INNER JOIN PUB.SDTZPA ON PUB.SDTPRA.zpanum = PUB.SDTZPA.zpanum) INNER JOIN PUB.SPAZPA ON PUB.SDTZPA.zpacod = PUB.SPAZPA.zpacod', \
            "PUB.SDTPRA.proref='%s'"%proref):
            if zpa['PUB.SPAZPA.zpatyp']=='2':
                logging.debug("%s = %s (zpavalnum)"%(zpa['PUB.SDTZPA.zpacod'],zpa['PUB.SDTZPA.zpavalnum']))
                results[zpa['PUB.SDTZPA.zpacod']] = zpa['PUB.SDTZPA.zpavalnum']
            else:
                logging.debug("%s = %s (zpaval)"%(zpa['PUB.SDTZPA.zpacod'],zpa['PUB.SDTZPA.zpaval']))
                results[zpa['PUB.SDTZPA.zpacod']] = zpa['PUB.SDTZPA.zpaval']
        #Codes Clients
        '''
            Règles :- si OF à la commande (clicod <> None):
              - si ref client du client de la commande
              - sinon rien
            - si pas OF à la commande :
              - si ref client coché client principal (souvent Toto)
              - sinon rien
                '''
        if clicod is None:
            #On va rechercher alors s'il existe un client principal pour ce produit
            code_client = self.select_one( \
                    ['PUB.SDTCLP.procliref'], \
                    'PUB.SDTCLP', \
                    "PUB.SDTCLP.clpprccon = 1 AND PUB.SDTCLP.proref = '%s'"%proref \
                    )
        else:
            #On va chercher le lien produit-client
            code_client = self.select_one( \
                    ['PUB.SDTCLP.procliref'], \
                    'PUB.SDTCLP', \
                    "PUB.SDTCLP.clicod = '%s' AND PUB.SDTCLP.proref = '%s' AND PUB.SDTCLP.datann is null"%(clicod, proref) \
                    )
        results.update(code_client)
        return results

    def get_matricules(self, stecod, seccod, ssecod, restypcod):
        '''Renvoie la liste des matricules
        stecod      :   code société (ex : '07')
        seccod      :   section (ex : '7PM')
        ssecod      :   sous-section (ex : '7PM')
        restypcod      :   type de resssource (ex : 'HO')
        '''
        return self.select_all( \
            ['PUB.SDTRES.rescod', 'PUB.SDTRES.resdes'], \
            "(PUB.SDTSEC INNER JOIN PUB.SDTSRE ON PUB.SDTSEC.secnumenr = PUB.SDTSRE.secnumenr) INNER JOIN PUB.SDTRES ON PUB.SDTSRE.resnumenr = PUB.SDTRES.resnumenr", \
            "PUB.SDTRES.stecod='%s' AND PUB.SDTSEC.seccod='%s' AND PUB.SDTSEC.ssecod='%s' AND PUB.SDTRES.restypcod='%s'"%(stecod, seccod, ssecod, restypcod))

    def get_printers(self, pgecod):
        '''renvoie la liste des imprimantes
            gpecod  :   position géographique des imprimantes
        '''
        return self.select_all( \
            ['PUB.SYSLPT.lpt', 'PUB.SYSLPT.lptlib', 'PUB.SYSLPT.lptcmdwin'], \
            "PUB.SYSLPT", \
            "PUB.SYSLPT.pgecod = '%s'"%(pgecod))

    def status(self):
        '''Renvoie le status
        '''
        return True

    def format_suivi(self, datas):
        '''Retourne une ligne de texte avec le suivi de la production au format SilverCS
        '''
        valid_datas = {}
        for k,v in datas.items():
            valid_datas[k.replace('.','_')] = v
        with open(self.json_format_suivi, 'r') as file:
            suivi = json.loads(file.read())
        logging.debug("valid_datas : %s"%valid_datas)
        logging.debug("suivi : %s"%suivi)
        return ";".join([x.format(**valid_datas) if isinstance(x,str) else str(x) for x in suivi])

    #### POUR COLISAGE

    def get_detail_bps(self, lprnumbps = [], stecod = '07', liecod = '7SIGNY'):
        now = time.time()
        if not isinstance(lprnumbps, list):
            lprnumbps = [lprnumbps]
        bps_lignes =  self.select_all(\
            "SELECT PUB.SVLPRE.lprnumbp, \
            PUB.SVLPRE.cdenum, PUB.SVLPRE.cdenumsui, PUB.SVLPRE.cdlposte, PUB.SVLPRE.cdlposts, \
            PUB.SVLPRE.clicodliv, PUB.SVLPRE.etsnumliv, \
            PUB.SVLPRE.proref, PUB.SVLPRE.procliref, PUB.SVLPRE.indnumenr, \
            PUB.SVLPRE.trpfoucod, \
            PUB.SVLPRE.lprcdecli, \
            PUB.SVLPRE.lprqtp, PUB.SVLPRE.lprqtl, \
            PUB.SVLPRE.lprpdsuni, PUB.SVLPRE.lprpdsuniq, PUB.SVLPRE.lprvoluni, PUB.SVLPRE.lprvoluniq, \
            PUB.SVLPRE.lprembpro, PUB.SVLPRE.lprembqte, PUB.SVLPRE.lprembpds, PUB.SVLPRE.lprembvol, \
            PUB.SVLPRE.lprtri, \
            PUB.SVLPRE.cdestatut \
            FROM PUB.SVLPRE \
            WHERE PUB.SVLPRE.lprnumbp IN (%s) AND PUB.SVLPRE.stecod = '%s' AND PUB.SVLPRE.liecod = '%s'"%(",".join(["'%s'"%n for n in lprnumbps]), stecod, liecod))
        logging.info("1er requete : %s"%(time.time()-now))
        now = time.time()
        if bps_lignes:
            cdes = []
            for ligne in bps_lignes:
                cde = (ligne['PUB_SVLPRE_cdenum'], ligne['PUB_SVLPRE_cdenumsui'])
                if cde not in cdes:
                    cdes.append(cde)
            notes = {}
            _notes = self.select_all( \
                "SELECT PUB.SVCEBA.cdenum, PUB.SVCEBA.cdenumsui, PUB.SDTBLN.blntxt \
                FROM PUB.SVCEBA INNER JOIN PUB.SDTBLN ON PUB.SVCEBA.blnnum = PUB.SDTBLN.blnnum \
                WHERE PUB.SVCEBA.cdenum in %s AND PUB.SDTBLN.txttyp = '1'"%str(tuple([cde[0] for cde in cdes]))
                )
            for cde in cdes:
                for note in [note for note in _notes if note['PUB_SVCEBA_cdenum'] == cde[0] and note['PUB_SVCEBA_cdenumsui']== cde[1]]:
                    if cde in notes:
                        notes[cde]['PUB_SDTBLN_blntxt'] += " " + note['PUB_SDTBLN_blntxt']
                    else:
                        notes[cde]={'PUB_SDTBLN_blntxt': note['PUB_SDTBLN_blntxt']}
            logging.debug("notes : %s"%notes)
            for cde, note in notes.items():
                for ligne in bps_lignes:
                    if cde == (ligne['PUB_SVLPRE_cdenum'], ligne['PUB_SVLPRE_cdenumsui']):
                        ligne.update(note)
        logging.info("autres requete : %s"%(time.time()-now))
        return bps_lignes

    def get_detail_bps_old(self, lprnumbps = [], stecod = '07', liecod = '7SIGNY'):
        if not isinstance(lprnumbps, list):
            lprnumbps = [lprnumbps]
        # LE FAIT DE LIER LES SDTBLN A FORTEMENT DETERIORER L'efficacité!!!
        # A TESTER en 2 FOIS !
        return self.select_all(\
            "SELECT \
                PUB.SVLPRE.lprnumbp, \
                PUB.SVLPRE.cdenum, PUB.SVLPRE.cdenumsui, PUB.SVLPRE.cdlposte, PUB.SVLPRE.cdlposts, \
                PUB.SVLPRE.clicodliv, PUB.SVLPRE.etsnumliv, \
                PUB.SVLPRE.proref, PUB.SVLPRE.procliref, PUB.SVLPRE.indnumenr, \
                PUB.SVLPRE.trpfoucod, \
                PUB.SVLPRE.lprqtp, PUB.SVLPRE.lprqtl, \
                PUB.SVLPRE.lprpdsuni, PUB.SVLPRE.lprpdsuniq, PUB.SVLPRE.lprvoluni, PUB.SVLPRE.lprvoluniq, \
                PUB.SVLPRE.lprembpro, PUB.SVLPRE.lprembqte, PUB.SVLPRE.lprembpds, PUB.SVLPRE.lprembvol, \
                PUB.SVLPRE.lprtri, \
                PUB.SVLPRE.cdestatut, \
                PUB.SDTBLN.blntxt \
            FROM PUB.SVLPRE INNER JOIN (PUB.SVCEBA LEFT JOIN PUB.SDTBLN ON PUB.SVCEBA.blnnum = PUB.SDTBLN.blnnum) ON ((PUB.SVLPRE.cdenumsui = PUB.SVCEBA.cdenumsui) AND  (PUB.SVLPRE.cdenum = PUB.SVCEBA.cdenum)) \
            WHERE \
                PUB.SVLPRE.lprnumbp IN (%s) \
                AND PUB.SVLPRE.stecod = '%s' \
                AND PUB.SVLPRE.liecod = '%s' \
                AND (PUB.SDTBLN.txttyp = '1' OR PUB.SDTBLN.txttyp IS NULL) \
                "%(",".join(["'%s'"%n for n in lprnumbps]), stecod, liecod)
            )
            #'PUB.SVLPRE.lprdatbes','PUB.SVLPRE.lprdatacc', \ Pb de format de date!!!!!! il faudra définir un sérialiseur pour les dates (ou jsonsimple)

    def get_ofs(self, typof = None, ofetat = '1', cdenum = None, stecod = '07', proref = None, prdmod = None, prscod = None):
        '''Renvoie la listes des commandes sous format d'un dict
            selon
            - typof (optionel)  "CDE", "OFK", "OFM", "OFP", "ST"
            - ofetat (optionel, "1" (valeur par defaut) = non débuté, "4" = soldé )
            - cdenum (optionel, pour pas de cdenum : mettre "")
            - prdmod (optionel) "1" : MRP, "2" : à la cde,  "3" : Flux tiré, "4" : Kanbans
        '''

        req = f"SELECT \
                PUB.SOFA.ofnum, \
                PUB.SOFA.typof, \
                PUB.SOFA.ofetat, \
                PUB.SOFA.ofref, \
                PUB.SOFA.datcre, \
                PUB.SOFB.proref, \
                PUB.SDTPRA.prodesmin, \
                PUB.SOFB.ofbqteini, \
                PUB.SOFB.ofbqterea, \
                PUB.SOFB.cdenum, \
                PUB.SOFB.clicod \
               FROM PUB.SOFA \
                INNER JOIN PUB.SOFB ON PUB.SOFA.ofanumenr = PUB.SOFB.ofanumenr \
                INNER JOIN PUB.SDTPRC ON PUB.SOFB.indnumenr = PUB.SDTPRC.indnumenr \
                INNER JOIN PUB.SDTPRB ON PUB.SDTPRC.varnumenr = PUB.SDTPRB.varnumenr \
                INNER JOIN PUB.SDTPRA ON PUB.SDTPRB.pronumenr = PUB.SDTPRA.pronumenr \
               WHERE \
                (PUB.SOFA.stecod = '{stecod}') \
                AND (PUB.SOFA.datann IS NULL) \
                "
        if typof is not None:
            req += f" AND (PUB.SOFA.typof = '{typof}')"
        if ofetat is not None:
            req += f" AND (PUB.SOFA.ofetat = '{ofetat}')"
        if cdenum is not None:
            req += f"  AND (PUB.SOFB.cdenum = '{cdenum}')"
        if proref is not None:
            req += f"  AND (PUB.SOFB.proref = '{proref}')"
        if prdmod is not None:
            req += f" AND (PUB.SDTPRA.prdmod = '{prdmod}')"
        if prscod is not None:
            req += f" AND (PUB.SDTPRC.prscod = '{prscod}')"
        return self.select_all(req)

    def get_encours(self, enctyp = None, proref = None, encstatut = "1", stecod = "07"):
        '''Renvoie la liste des encours de stock sous forme d'un dict
            enctyp : "7" : Cdes clients
            encstatus : "1" (valeur par defaut) : ferme "4" : "prévisionnel"
        '''
        req = f"SELECT \
                    PUB.STOENC.proref, \
                    PUB.STOENC.enctyp, \
                    PUB.STOENC.encqteini, \
                    PUB.STOENC.encqterea, \
                    PUB.STOENC.encdoc \
                FROM PUB.STOENC \
                WHERE \
                    PUB.STOENC.stecod = '{stecod}' \
                    AND PUB.STOENC.encstatut = '{encstatut}'"
        if enctyp is not None:
            req += f" AND PUB.STOENC.enctyp = '{enctyp}'"
        if proref is not None:
            req += f" AND PUB.STOENC.proref = '{proref}'"
        return self.select_all(req)

    def get_cde_datas(self, cdenum):
        '''Renvoie les infos de la commande client
        '''
        req = f"SELECT PUB.SVCEBA.clicodliv FROM PUB.SVCEBA WHERE PUB.SVCEBA.cdenum = '{cdenum}'"
        result = self.select_all(req)
        if result:
            return result[0]
        else:
            return {}


    def set_cdenum_of(self, ofnum, cdenum):
        '''Met à jour la commande rattachée à l'OF
        '''
        clicod = self.get_cde_datas(cdenum).get('PUB_SVCEBA_clicodliv')
        if clicod:
            req = f"UPDATE PUB.SOFB SET cdenum = '{cdenum}' , clicod = '{clicod}' WHERE ofanumenr = (SELECT PUB.SOFA.ofanumenr FROM PUB.SOFA WHERE PUB.SOFA.ofnum = '{ofnum}')"
            self.execute_sql(req, mode = 'other')
        else:
            logging.error("Can't get clicod.")

    def get_produits_emplacement(self, emplacement, only_on_stock = False):
        '''Renvoie la liste des produits sur un emplacement
        '''
        req = "SELECT PUB.SDTPRA.proref, PUB.SDTPRA.prdmod, PUB.SDTZPA.zpacod, PUB.STOLIE.stoqte, PUB.STOLIE.bescde, PUB.STOLIE.besfab, PUB.STOLIE.encfab, PUB.STOLIE.stoqteaff "
        req += "FROM PUB.SDTPRA INNER JOIN PUB.SDTZPA ON PUB.SDTPRA.zpanum = PUB.SDTZPA.zpanum "
        req += "INNER JOIN PUB.STOLIE ON PUB.STOLIE.proref = PUB.SDTPRA.proref "
        #req += "INNER JOIN PUB.SDTPRC ON PUB.SDTPRC.proref = PUB.SDTPRA.proref "
        req += f"WHERE PUB.SDTZPA.zpacod = '7EMP' and PUB.SDTZPA.zpaval = '{emplacement}' "
        if only_on_stock:
            req += "AND PUB.STOLIE.stoqte > 0"
        return self.select_all(req)


    def set_prdmod(self, proref, prdmod):
        ''' Modifie le mode de production (prdmod)
            '1'     MRP
            '2'     A la commande
        '''
        req = f"UPDATE PUB.SDTPRA SET prdmod = '{prdmod}' WHERE proref = '{proref}'"
        self.execute_sql(req,'other')

    def get_produits(self, promotdir = None, stecod = '07', indlctcon = None):
        '''Renvoie la liste des produits selon critères (TODO : élargir critères)
        '''
        req = "SELECT PUB.SDTPRA.proref, PUB.SDTPRA.prdmod, PUB.SDTPRC.nclnivmax "
        req += "FROM PUB.SDTPRA INNER JOIN PUB.SDTPRB ON PUB.SDTPRA.proref = PUB.SDTPRB.proref "
        req += "INNER JOIN PUB.SDTPRC ON PUB.SDTPRC.varnumenr = PUB.SDTPRB.varnumenr "
        req += "WHERE PUB.SDTPRA.datann IS NULL"
        req += f" AND PUB.SDTPRA.stecod = '{stecod}'"
        if promotdir:
            req += f" AND PUB.SDTPRA.promotdir = '{promotdir}' "
        if indlctcon is not None:
            req += f" AND PUB.SDTPRC.indlctcon = {-1 if indlctcon else 0}" # Ne fonctionne pas !!!!!
        return self.select_all(req)

    def get_produits_zpa(self, zpacod, zpaval = None):
        '''Renvoie la liste des produits selon Zone paramètrable 
        '''
        req = "SELECT PUB.SDTPRA.proref, PUB.SDTPRA.prdmod, PUB.SDTZPA.zpacod, PUB.SDTZPA.zpaval "
        req += "FROM PUB.SDTPRA INNER JOIN PUB.SDTZPA ON PUB.SDTPRA.zpanum = PUB.SDTZPA.zpanum "
        req += "WHERE PUB.SDTPRA.datann IS NULL "
        req += f" AND PUB.SDTZPA.zpacod = '{zpacod}' "
        if zpaval:
            req += f" and PUB.SDTZPA.zpaval = '{zpaval}' "
        return self.select_all(req)

    def get_stock(self, proref, liecod = None, no_zero = False):
        '''Renvoie la liste des stocks
        '''
        req = "SELECT PUB.STOLIE.liecod, PUB.STOLIE.stoqte, PUB.STOLIE.bescde, PUB.STOLIE.besfab, PUB.STOLIE.encfab, PUB.STOLIE.stoqteaff "
        req += "FROM PUB.STOLIE "
        req += f"WHERE PUB.STOLIE.proref = '{proref}' "
        if no_zero:
            req += " AND PUB.STOLIE.stoqte <> 0 AND PUB.STOLIE.bescde <> 0 AND PUB.STOLIE.besfab <> 0 AND PUB.STOLIE.encfab <> 0 "
        return self.select_all(req)


    def get_produits_stock(self, proref = None, liecod = '7SIGNY', prdmod:str = None, prscod:str = None, where:str = None):
        """Renvoie la list des produits et leur stock selmon critères
            prdmod  :   Type de fabrication ('1' : MRP (=Stock), '2' : A la commande)
            prscod  :   Statut du produit (ex : '10' : Décors à la commande, '12' : peinture à la commande)
            where   :   Autre clause where de la requete
            Note : si une valeur commence par '<>' ou '>' ou ... , alors la clause est <> ou > ou ...
        """
        req = f"""SELECT
                PUB.SDTPRA.prdmod,
                PUB.SDTPRA.proref,
                PUB.SDTPRA.prodes1,
                PUB.SDTPRA.prodes2,
                PUB.SDTPRA.prodesmin,
                PUB.SDTPRA.zpanum,
                PUB.SDTPRC.prscod,
                PUB.STOLIE.stoqte,
                PUB.STOLIE.stoqteaff,
                PUB.STOLIE.encfab,
                PUB.STOLIE.bescde,
                PUB.STOLIE.besfab
            FROM
                ((PUB.SDTPRA INNER JOIN
                PUB.SDTPRB ON PUB.SDTPRA.pronumenr = PUB.SDTPRB.pronumenr) INNER JOIN
                PUB.SDTPRC ON PUB.SDTPRB.varnumenr = PUB.SDTPRC.varnumenr) INNER JOIN PUB.STOLIE ON PUB.SDTPRC.indnumenr = PUB.STOLIE.indnumenr
            WHERE PUB.STOLIE.liecod = '{liecod}' """
        if proref:
            req += f" AND {self.add_clause('PUB.SDTPRA.proref', proref)}"
        if prdmod:
            req += f" AND {self.add_clause('PUB.SDTPRA.prdmod',prdmod)}"
        if prscod:
            req += f" AND {self.add_clause('PUB.SDTPRC.prscod',prscod)}"
        if where:
            req += f" AND {where}"
        return self.select_all(req)

    def set_production_mode(self, produit, prdmod:str):
        '''Change le mode de production d'un produit
        prdmod :    '1' : MRP (=Stock)
                    '2' : A la commande
                    '3' : Flux tiré (non utilisé)
                    '4' : Kanban (non utilisé)
        '''
        if type(produit)==str:
            produit = self.get_produits_stock(proref = produit)[0]
        req = None
        if produit.get('PUB_SDTPRC_prscod')=='10':# PF decors à la commande
            req = f"UPDATE PUB.SDTPRA SET prdmod = '{prdmod}' WHERE proref = '{produit.get('PUB_SDTPRA_proref')}'"
        elif produit.get('PUB_SDTPRC_prscod')=='12':# PF peinture à la commande
            if prdmod == '2':# à la commande"
                prodes2 = produit.get("PUB_SDTPRA_prodes2")[:34]+" "*(34-len(produit.get("PUB_SDTPRA_prodes2")))+"*"
                prodes2 = prodes2.replace("'","''")
                req = f"UPDATE PUB.SDTPRA SET prodes2 = '{prodes2}' WHERE proref = '{produit.get('PUB_SDTPRA_proref')}'"
            elif prdmod == '1':# MRP = stock"
                if len(produit.get("PUB_SDTPRA_prodes2"))>=35 and produit.get("PUB_SDTPRA_prodes2")[34]=='*':
                    prodes2 = produit.get("PUB_SDTPRA_prodes2")[:34]
                    req = f"UPDATE PUB.SDTPRA SET prodes2 = '{prodes2}' WHERE proref = '{produit.get('PUB_SDTPRA_proref')}'"
        if req:
            self.execute_sql(req,'other')
        if prdmod=='2':# à la commande
            req = f"UPDATE PUB.SDTPRB SET stomin  = 0, stomax = 0, stosec = 0 WHERE proref = '{produit.get('PUB_SDTPRA_proref')}'"
            self.execute_sql(req,'other')
            req = f"UPDATE PUB.SDTZPA SET zpaval = 'CAGE' WHERE zpanum = {produit.get('PUB_SDTPRA_zpanum')} AND zpacod = '7EMP'"
            self.execute_sql(req,'other')
        elif prdmod=='1':# MRP=stock
            if self.get_emplacement(produit)=='CAGE':
                req = f"UPDATE PUB.SDTZPA SET zpaval = 'STK*' WHERE zpanum = {produit.get('PUB_SDTPRA_zpanum')} AND zpacod = '7EMP'"
                self.execute_sql(req,'other')

    def get_emplacement(self, produit)-> str:
        '''renvoie l'emplacement d'un produit
        produit     :   str : proref
        dict        :   renvoie d'une requete avec champ zpanum
        '''
        if type(produit)==str:
            req = f"""SELECT
                    PUB.SDTZPA.zpaval
                FROM
                    PUB.SDTPRA INNER JOIN
                    PUB.SDTZPA ON PUB.SDTPRA.zpanum = PUB.SDTZPA.zpanum
                WHERE PUB.SDTPRA.proref = '{produit}' AND PUB.SDTZPA.zpacod = '7EMP'"""
        elif type(produit)==dict:
            req = f"""SELECT
                    PUB.SDTZPA.zpaval
                FROM
                    PUB.SDTZPA
                WHERE PUB.SDTZPA.zpanum = {produit.get('PUB_SDTPRA_zpanum')} AND PUB.SDTZPA.zpacod = '7EMP'"""
        try:
            req
        except NameError:
            raise Exception("Error on get_emplacement : produit must be str or dict.") 
        else:
            results = self.select_all(req)
            if results:
                return results[0].get('PUB_SDTZPA_zpaval')




    @staticmethod
    def add_clause(field:str, val)->str:
        """ Renvoie Une clause where du type field ope [']val[']
        si val commence par
            - '<>'   :   ope = '<>'
            - '>'   :   ope = '>'
            - '>='  :   ope = '>="
            - ...
            - else : ope = '='
            Note : si val est numérique, ces opérateur ne fonctionnent pas.
        """#On aurait pu aussi le faire à la mode mongo : {'$gt':42}
        opes = {'<>','>', '>=', '<', '<='}
        operator = '=' #default
        if type(val)==str:
            for ope in sorted(opes, key=lambda ope:-len(ope)):
                if val[:len(ope)] == ope:
                    operator = ope
                    val = val[len(ope):]
                    break
            val=f"'{val}'"
        return f" {field} {operator} {val} "

    def get_gammes(self, proref, stecod = "07"):
        '''renvoie la liste ordonnée des gammes d'un produit
        '''
        req = f'''
                SELECT PUB.SDTPRC.proref, PUB.SDTPRD.prdordnum, PUB.SDTPRD.gamcod
                FROM PUB.SDTPRC INNER JOIN PUB.SDTPRD ON PUB.SDTPRC.indnumenr = PUB.SDTPRD.indnumenr
                WHERE PUB.SDTPRC.proref='{proref}' AND PUB.SDTPRD.stecod='{stecod}'
                ORDER BY PUB.SDTPRD.prdordnum
        '''
        return self.select_all(req)

    def get_production(self, jour_production, codes_mvts = ['12', '12M'], stecod = '07', liecod = '7SIGNY'):
        '''Renvoie le détail d'une journée de production
        '''
        return self.get_stomvs(jour_production, codes_mvts, stecod, liecod)

    def get_stomvs(self, jour, codes_mvts, stecod = '07', liecod = '7SIGNY', where = None):
        '''renvoie la liste des mouvements de stock
        jour    datetime.date
        codes_mvts  :   code mouvement ou liste de 
        where       :   clause WHERE à ajouter à la requete
        '''
        if type(codes_mvts)!= list:
            codes_mvts = [codes_mvts]
        req = "SELECT PUB.STOMVS.proref, PUB.STOMVS.mvsqte, PUB.SDTPRA.prdfamcod, PUB.SPAFAM.famlib, PUB.SDTPRA.prodesmin "
        #req += ",PUB.SDTPRB.varnumenr, PUB.SDTPRC.indnumenr"
        req += """
                FROM PUB.STOMVS 
                    INNER JOIN 
                        PUB.SDTPRC
                        ON PUB.STOMVS.indnumenr = PUB.SDTPRC.indnumenr
                    INNER JOIN 
                        PUB.SDTPRB
                        ON PUB.SDTPRB.varnumenr = PUB.SDTPRC.varnumenr
                    INNER JOIN
                        PUB.SDTPRA
                        ON PUB.SDTPRA.pronumenr = PUB.SDTPRB.pronumenr
                    INNER JOIN
                        PUB.SPAFAM
                        ON PUB.SPAFAM.famcod = PUB.SDTPRA.prdfamcod 
            """
        req += f"WHERE PUB.STOMVS.mvsdat = '{jour:%Y-%m-%d}' "
        if stecod:
            req += f" AND PUB.STOMVS.stecod = '{stecod}'"
        if liecod:
            req += f" AND PUB.STOMVS.liecod = '{liecod}'"
        if codes_mvts:
            req += f" AND PUB.STOMVS.mvscod IN (" +','.join([f"'{code}'" for code in codes_mvts])+")"
        if where:
            req += f" AND {where} "
        return self.select_all(req)      


    def invoics_errors(self, edimsg='7INV'):
        '''Renvoie la liste des factures edi en erreur
        '''
        req = f"""SELECT PUB.SEDMSE.msedocnum, PUB.SEDMSE.datcre
                FROM PUB.SEDMSE
                WHERE PUB.SEDMSE.edimsg = '{edimsg}'
                AND PUB.SEDMSE.datann IS NULL"""
        factures = self.select_all(req)
        #Extraction du détail de l'erreur
        for facture in factures:

            req = f"""SELECT TOP 1 PUB.SEDJRD.jrdmsglib, PUB.SEDJRD.msgcod, PUB.SEDJRD.proref
                    FROM PUB.SEDJRD
                    WHERE PUB.SEDJRD.edimsg  = '{edimsg}'
                    AND PUB.SEDJRD.jrddocnum = '{facture.get('PUB_SEDMSE_msedocnum')}'
                    ORDER BY PUB.SEDJRD.jrenumenr DESC"""
            try:
                facture['details'] = self.select_all(req)[0]
                edidon = facture['details'].get('1 PUB_SEDJRD_jrdmsglib',"-").split('-')[1]
            except Exception as e:
                logging.warning(f"Erreur getting details error invoice : {e}")
            else:
                req = f"""SELECT PUB.SEDDON.edidonlib
                            FROM PUB.SEDDON
                            WHERE PUB.SEDDON.edidon = '{edidon}'
                                    """
                facture['details'].update(self.select_all(req)[0])
        return factures


    def produits_toto_errors(self, clicod = '799308', etsnum = "001", stecod = '07'):
        '''Renvoie la liste des lignes de commande avec produit sans code client
        '''
        req = f"""SELECT PUB.SVCPBA.cdenum,
                    PUB.SVCPBA.clicodliv, PUB.SVCPBA.etsnumliv,
                    PUB.SVCPBA.proref, PUB.SVCPBA.procliref
                FROM PUB.SVCPBA LEFT JOIN PUB.SDTCLP
                    ON (PUB.SVCPBA.proref = PUB.SDTCLP.proref
                    AND PUB.SVCPBA.etsnumliv = PUB.SDTCLP.etsnum
                    AND PUB.SVCPBA.clicodliv = PUB.SDTCLP.clicod)
                WHERE
                    PUB.SVCPBA.stecod = '{stecod}'
                    AND PUB.SVCPBA.clicodliv = '{clicod}'
                    AND PUB.SVCPBA.etsnumliv = '{etsnum}'
                    AND PUB.SVCPBA.cdldatsol IS NULL
                    AND (PUB.SDTCLP.clpprccon IS NULL OR PUB.SDTCLP.clpprccon=0)
                """
        return self.select_all(req)

    def doublons_ref_client_principal(self):
        '''Renvoie la liste des produits avec plusieurs clients principaux
        '''
        req = """
            SELECT PUB.SDTCLP.proref, Count(PUB.SDTCLP.clpprccon) AS CompteDeclpprccon
            FROM PUB.SDTCLP
            WHERE PUB.SDTCLP.clpprccon = 1 AND PUB.SDTCLP.datann IS NULL AND PUB.SDTCLP.proref LIKE '7%' AND PUB.SDTCLP.clicod LIKE '7%'
            GROUP BY PUB.SDTCLP.proref
            HAVING Count(PUB.SDTCLP.clpprccon)>1
            """
        return self.select_all(req)


    def get_envirronement_variable(self, code)-> str:
        ''' Renvoie la donnée liée à la variable d'envirronement code
        '''
        req = f"""
            SELECT PUB.SYSENV.envtxt
            FROM PUB.SYSENV
            WHERE PUB.SYSENV.envcod = '{code}'
            """
        try:
            return self.select_all(req)[0]['PUB_SYSENV_envtxt']
        except:
            return None
    
    def set_envirronement_variable(self, code, envtxt):
        '''Met à jour une variable d'envirronnement
        '''
        req = f"""
            UPDATE PUB.SYSENV
            SET envtxt = '{envtxt}'
            WHERE envcod = '{code}'
        """
        return self.execute_sql(req, mode = 'other')

    def get_cnuf(self, stecod = '07'):
        """Renvoie le CNUF de la société
        """
        req = f"""
            SELECT PUB.SPAST.gcdcnuf
            FROM PUB.SPAST
            WHERE PUB.SPAST.stecod = '{stecod}'
        """
        try:
            return self.select_all(req)[0]['PUB_SPAST_gcdcnuf']
        except:
            return None

    @staticmethod
    def get_ean13_checksum(ean12:str)->str:
        """Renvoie le 13eme caractère d'un EAN13 à partir des 12 premiers
        """
        assert len(ean12)==12,f"ean12 must have 12 digits.ean12 = {ean12}"
        assert ean12.isnumeric(), f"ean12 must contain only digits. ean12 = {ean12}"
        checksum = 0
        for index in range(len(ean12)):
            checksum += int(ean12[index])*(1+index%2*2)
        if checksum%10 == 0:
            return "0"
        else:
            return str(10 - checksum%10)

    def get_new_gencod(self,stecod = "07")->str:
        '''Renvoie un nouveau gencod disponible : 
            le suivant de la VE 
        '''
        #recherche du dernier code
        if not (envtxt:=self.get_envirronement_variable(f"GENCOD{stecod}")):
            envtxt = self.get_envirronement_variable(f"GENCOD")
            code_ve = f"GENCOD"
        else:
            code_ve = f"GENCOD{stecod}"
        last_gencod_article = int(envtxt[1:])
        #Calcul de la clef
        cnuf = self.get_cnuf(stecod)
        loop = True
        while loop:
            last_gencod_article += 1
            article = str(last_gencod_article)
            ean12 = cnuf + article
            new_ean13 = ean12 + self.get_ean13_checksum(ean12)
            loop = self.get_proref_by_gencod(new_ean13) #Si gencod existe dans la base : on cherche un nouveau
        #Mise à jour de la VE
        self.set_envirronement_variable(code_ve, envtxt[0]+article)
        #Check gencod not exist
        #TODO
        return new_ean13

    def get_gencod(self, proref)->str:
        '''Renvoie le gencod d'un produit
        '''
        req = f"""
            SELECT PUB.SDTPRB.gencod
            FROM PUB.SDTPRB
            WHERE PUB.SDTPRB.proref = '{proref}'
        """
        try:
            return self.select_all(req)[0]['PUB_SDTPRB_gencod']
        except:
            return None

    def set_gencod(self, proref, gencod = None, force = False):
        """ Attribut un gencod à la proref.
        Si gencod est omis : un nouveau gencod
        Attention : pas de gestion des indices
        """
        if force or not self.get_gencod(proref):
            if gencod is None:
                gencod = self.get_new_gencod()
            req = f"""
                UPDATE PUB.SDTPRB
                SET gencod = '{gencod}'
                WHERE proref = '{proref}'
            """
            self.execute_sql(req, mode = 'other')
            return gencod
        else:
            logging.warning(f"{proref} a déjà un gencod. Pour le modifier, utiliser l'option force =True ")

    #def get_proref_by_gencod(self, gencod:str)->list[dict]: non compatible python 3.8!!!
    def get_proref_by_gencod(self, gencod):
        '''Renvoie la list des produits associée à un gencod
        '''
        req = f"""
            SELECT PUB.SDTPRB.proref, PUB.SDTPRB.gencodpcb
            FROM PUB.SDTPRB
            WHERE PUB.SDTPRB.gencod = '{gencod}'
        """
        return self.select_all(req)

class OdbcSilverCS(SilverCS):
    '''Une base de données Silver CS accéssible via odbc
    '''
    def __init__(self, DNS = "DSN=SILV-EXP;UID=SYSPROGRESS;PWD=SYSPROGRESS", *args, **kwargs):
        '''Initialisation :
            - DNS   :   chaine DNS (ex : "DNS=MaBase;UID=LOGIN;PWD=PASSWORD")
        '''
        self.DNS = DNS
        try:
            self.conn = pyodbc.connect(DNS)
        except Exception as e:
            logging.error(f"Error initialising ODBC connection : {DNS} : {e}")
        SilverCS.__init__(self, *args, **kwargs)

    def __str__(self):
        return "OdbcSilverCS(%s)"%self.DNS

    def execute_sql(self, req, mode = None):
        '''Execute une requête sql et retourne un curseur
        '''
        cursor = self.conn.cursor()
        cursor.execute(req)
        return cursor

    def fetchone(self, req):
        try:
            return self.execute_sql(req).fetchone()
        except:
            return {}

    def fetchall(self, req):
        try:
            return self.execute_sql(req).fetchall()
        except Exception as e:
            logging.error(f"Error with SQL : {req} : {e}")
            return []

    def scan_fields(self, field, value):
        '''Scan dans toute la base les enregistrements qui correspondent avec field == value
        '''
        #result = {}
        cursor = self.conn.cursor()
        for _field in cursor.columns():
            if _field[3] == field:
                table = _field[1]+"."+ _field[2]
                req = f"""SELECT * FROM {table}
                        WHERE {table}.{field} = '{value}'
                """
                #result[table] = self.select_all(req)
                yield (table, self.select_all(req))
        #return result

class HttpSilverCS(SilverCS):
    '''Une base de données Silver CS accéssible via http (via serveur flask : ./index.py)
        http    :   host:port/path
    '''
    def __init__(self, host = 'localhost', port = 50888, path = "silvercs", timeout = 30, user = None, password = None, *args, **kwargs):
        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self.auth = (user, password)
        SilverCS.__init__(self, *args, **kwargs)

    def __str__(self):
        return "HttpSilverCS(%s:%s/%s)"%(self.host,self.port, self.path)

    def execute_sql(self, req, mode = None):
        try:
            r = self.requests_get(f"/{self.path}?req={req}&mode={mode}")
            return r.json()
        except Exception as e :
            logging.error(f"Error with SQL : {req} : {r.text}")
            return []

    fetchall = execute_sql

    def fetchone(self, req):
        try:
            return self.execute_sql(req)[0]
        except IndexError:
            return {}

    def encode_dict(self, dict):
        '''Transforme les dates en string
        '''
        for k in dict:
            if isinstance(dict[k],(datetime.datetime, datetime.date)):
                dict[k]=dict[k].isoformat()
        return dict

    def export_suivi(self, datas):
        '''from a dict (datas) or string (json), export the production
        '''
        logging.info(f"Export suivi : datas = {datas}")
        if type(datas)==str:
            try:
                datas = json.loads(datas)
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Error decoding json :{e}")
                datas = None
        if datas:
            #production = self.encode_json(datas)
            #r = self.requests_get("/prod", params = {'datas' : production})
            production = self.encode_dict(datas)
            r = self.requests_get("/production", params = production)
            logging.debug(f"export_suivi : fin request : r={r}")
            if r is None:
                logging.error(f"export_suivi : Request error : None")
            elif r.text[:2] != "OK":
                logging.error(f"export_suivi : Request error : {r.text}")
            else:
                logging.debug("export_suivi : OK")
                return True

    def status(self):
        '''Renvoie le status (False | True) de la connection
        '''
        try:
            r = self.requests_get()
            return r.text=='Ok'
        except:
            return False

    def requests_get(self, url = "", params = None):
        '''Do a requests.get and return the response
            url         :   la fin de l'url (apres http://IP:port)
            params      :   datas
        '''
        logging.debug(f"request_get({url},params={params})")
        try:
            r = requests.get(f"http://{self.host}:{self.port}" + url, params = params, auth = self.auth, timeout = self.timeout)
        except Exception as e:
            logging.error(f"Error on request : {e}")
            r = None
        return r

    def get_srv_version(self):
        '''Renvoie le n° de version de l'application sur le serveur
        '''
        return self.requests_get("/version").text

class NoneSilverCS(SilverCS):
    '''Une fausse base de données qui ne renvoie que des exemples (ou rien)
    '''
    def __init__(self, *args, **kwargs):
        SilverCS.__init__(self, *args, **kwargs)
    def execute_sql(self, req):
        return []
    fetchall = execute_sql
    def fetchone(self, req):
        return {}
    def export_suivi(self, datas):
        pass


#Pour test
if __name__ == '__main__':
    silverCS = HttpSilverCS("192.168.0.6", 50888, user = "olfa", password = "montage08380")
    #produits = silverCS.get_produits_stock(prdmod = '<>2', prscod='10', where="(PUB.STOLIE.stoqte - PUB.STOLIE.stoqteaff)<=0")
    #silverCS.set_production_mode(produit = '7TD04000201B', prdmod = '1')
    #silverCS.set_production_mode(produit = '7TD04000201B', prdmod = '2')
    produits = silverCS.get_produits_stock(prdmod = '2', prscod='10', where="Disponible > 0 ")
    #produits2 = silverCS.get_produits_stock(where="(PUB.STOLIE.stoqte > PUB.STOLIE.bescde + PUB.STOLIE.besfab - PUB.STOLIE.encfab) ")
    pass