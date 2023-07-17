'''
Script qui va chercher dans les mouvements des kanbans
- ceux qui n'ont pas déjà été traités
- dont les références sont du type 2 passes (=ZPA 7SF2 = 'O')
- si le type de mouvement n'est pas une consommation

et génère un suivi de production (via api sur srv-tse:50888)
et envoie un email à qualite@olfa.fr si un contrôle n'est pas conforme.

Executer tous les jours par SRV-DEBIAN toutes les 10 minutes
Crontab : */10 7-16 * * 1-5 /usr/local/bin/python3 /home/administrateur/commun/ApplicationsOLFA/OKanbans/OTriggers/triggers.py
'''


import sys, os, datetime, socket
sys.path.append(os.path.join(sys.path[0],'..','OKanban'))
from bdd import BddOKanbans
from silvercs import HttpSilverCS
from smtp import Smtp
from FUTIL.my_logging import *
import markdown

my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
logging.info(f'OKanban Triggers start on {socket.gethostname()}')

bdd = BddOKanbans('192.168.0.11')
silverCS = HttpSilverCS("192.168.0.6", 50888, user = "olfa", password = "montage08380")
produit_2_passes = [p.get('PUB_SDTPRA_proref') for p in silverCS.get_produits_zpa("7SF2","O")]
smtp = Smtp('SRV-SQL', 25, 'courrier@olfa.fr', 'courrier@olfa.fr', "huit8\\_8", starttls=False)

def crt_suivi(proref, qte, date_prod = None, matricule = 'A', openum = '10'):
    ''' Crée un suivi de production sur le produit
    '''
    if date_prod is None:
        date_prod = datetime.date.today()
    ofs = silverCS.get_ofs(proref=proref, ofetat = None)
    ofs = [of for of in ofs if of.get('PUB_SOFA_typof').upper()=='OFK' and of.get('PUB_SOFA_ofetat') != '4']
    if len(ofs)>0:
        ofnum=ofs[0].get('PUB_SOFA_ofnum')
        suivi = {
            'date_prod' : date_prod,
            'matricule' : matricule,
            'PUB_SOFA_ofnum' : ofnum,
            'PUB_SOFD_openum' : openum,
            'PUB_SOFB_proref' : proref,
            'qterea' : qte,
            'etatof' : '2'
            }
        silverCS.export_suivi(suivi)
    else:
        raise Exception(f"N° d'OF non trouvé pour {proref}")

kanbans_errors = []

for kanban in bdd.get_kanbans(only_not_triggered=True):
    logging.debug(f"kanban not trigered : {kanban}")
    proref = kanban.get('proref')
    if kanban.get('conforme') == 'NOK':
        kanbans_errors.append(kanban)
    for mvt in kanban.get('mvts',[]):
        if mvt.get('triggered') == False:
            if mvt.get('type') == 'creation':
                logging.debug(f"création : {mvt}")
                if proref in produit_2_passes:
                    try:
                        crt_suivi(proref, mvt['qte'], mvt['date'])
                    except Exception as e:
                        logging.error(f"Erreur during crt_suivi : {e}")
                    else:
                        mvt['triggered'] = True
                else:
                    mvt['triggered'] = True
            elif mvt.get('type') == 'modification':
                logging.debug(f"modification : {mvt}")
                if proref in produit_2_passes:
                    try:
                        crt_suivi(proref, mvt['qte'], mvt['date'])
                    except Exception as e:
                        logging.error(f"Erreur during crt_suivi : {e}")
                    else:
                        mvt['triggered'] = True
                else:
                    mvt['triggered'] = True
            elif mvt.get('type') == 'consommation':
                logging.debug(f"consommation : {mvt}")
                mvt['triggered'] = True
    kanban['triggered'] = True
    for mvt in kanban.get('mvts',[]):
        if mvt.get('triggered') == False:
            kanban['triggered'] = False
    if kanban['triggered']:
        logging.info(f"Kanban {kanban['id']} is flaged as triggered.")
    else:
        logging.warning(f"Kanban {kanban['id']} fail to be triggered!!!")
    bdd.set_kanban_triggered(kanban)

# Email si kanbans non conforme
if kanbans_errors:
    txt = "Il existe des mesures de perçage non conforme : \n\n"
    for kanban in kanbans_errors:
        txt += f"## Id = {kanban.get('id')} : {kanban.get('proref')}\n"
        for key, mesure in kanban.get('mesures').items():
            if mesure.get('result')=='Faux':
                txt += f"> {key} : {mesure.get('value')} (doit être compris entre {mesure.get('mini')} et {mesure.get('maxi')})"
    smtp.send('frederic.thome@olfa.fr', "Contrôle des perçages", markdown.markdown(txt), type = 'html')
    smtp.send('qualite@olfa.fr', "Contrôle des perçages", markdown.markdown(txt), type = 'html')


