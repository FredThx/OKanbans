'''Une API pour OKanban

ca tourne sur : SRV-DEBIAN (okanban_api.service)

url : localhost:50890/okanban
'''
from flask import Flask, request
#from flask_cors import CORS
from flask_restful import abort, Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import datetime, json, re

from OKanban.bdd import BddOKanbans
from OKanban.nicelabel import HttpNiceLabel

from FUTIL.my_logging import *
my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
logging.info('OKanban API start')

app = Flask(__name__)
api = Api(app)

okanban_bdd = BddOKanbans('192.168.0.11')
okanban_printer = HttpNiceLabel('http://192.168.0.6:56425')
#okanban_printer_name = "IMP_TEST"
okanban_printer_name = "\\\\SRV-DATA\\ZEBRA PERCAGE"
okanban_etiquette = "ET_PER_API"

auth = HTTPBasicAuth()
users = {
    "olfa": generate_password_hash("Trone08")
}
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

okanban_api_parser = reqparse.RequestParser()
okanban_api_parser.add_argument('proref', type=str, required = True)
okanban_api_parser.add_argument('qte', type=int)
okanban_api_parser.add_argument('date', type=str)
okanban_api_parser.add_argument('remarques', type=str)
okanban_api_parser.add_argument('conforme', type=str)
okanban_api_parser.add_argument('operateur', type=str)
okanban_api_parser.add_argument('mesures', type=dict)

class OkanbanApi(Resource):
    @auth.login_required
    def get(self, proref):
        '''Renvoie la quantité par defaut des kanbans
        '''
        ref = okanban_bdd.get_references(proref)
        if ref is None or len(ref)==0:
            logging.error(f"Error on get_proref_qty : proref={proref}, ref={ref}")
            abort(404, message=f"{proref} doesn't existe.")
        else:
            ref = ref[0]
            logging.info(f"GET {proref}=>{ref.get('qte_kanban_plein')}")
            return ref.get('qte_kanban_plein')
        
    @auth.login_required
    def post(self):
        '''Création d'un kanban
        '''
        #args = request.get_json(force=True)
        args = okanban_api_parser.parse_args()
        args['conforme']= "OK" if args.get('conforme')=='-1' else "NOK"
        # todo : trier les mesures P1, R1, ...
        args['date'] = datetime.date.today().strftime("%d/%m/%Y")
        args['mesures'] = {cote : {k : float(v.replace(',','.')) if v.replace(',','.').isnumeric() else v for k, v in mesure.items()} for cote, mesure in args.get('mesures',{}).items()}
        #args['mesures']['controleur'] = args.get('operateur')
        #Creation d'un kanban
        id = okanban_bdd.set_kanban(proref=args['proref'], qte=args.get('qte'), type = "creation", mesures=args.get('mesures'), conforme = args.get('conforme'))
        try:
            #Imprime une étiquette kanban
            args['id'] = id
            args['mesures'] = ', '.join([f"{cote}:{mesure}" for cote, mesure in args.get('mesures',{}).items()])
            args['printer'] = okanban_printer_name
            args['date_creation'] = args['date']
            del args['date']
            args['qty'] = 1 # Nb d'étiquettes
            args['etiquette'] = okanban_etiquette
            print(args)
            #Bricolo pour dépanner
            args['mesures'] = args['mesures'].replace("'",'"')
            args['mesures'] = "{" + args['mesures'] + "}"
            args['mesures'] = re.sub(r'((?:[[PR][0-9]{1,2}|X[12DP])):',r'"\1":', args['mesures'])
            #for key in [f'P{i}' for i in range(12)]+[f'R{i}' for i in range(12)] + ['XD','X1', 'X2', 'XP']:
            #    args['mesures'] = args['mesures'].replace(key, '"'+key+'"')
            args['mesures'] = json.loads(args['mesures'])########
            args['mesures'] = str({cote : mesure.get('value') for cote, mesure in args.get('mesures').items()})
            okanban_printer.print(**args)
        except Exception as e:
            logging.error(e)
            okanban_bdd.delete_kanban(id)
            return f"Error on API OKanbans: {e}", 400
        else:
            logging.info(f"POST : Création kanban : {args}")
            return "OK", 200 #TODO : renvoyer Id (et le gérer dans access!!)

api.add_resource(OkanbanApi, "/okanban/qte/<proref>", "/okanban")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=50890, debug=False)