'''Une API pour OKanban

ca tourne sur : SRV-DEBIAN (okanban_api.service)

url : localhost:50890/okanban
'''
from flask import Flask, request
#from flask_cors import CORS
from flask_restful import abort, Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from OKanban.bdd import BddOKanbans
from OKanban.nicelabel import HttpNiceLabel
from OKanban.environnement import *
from OKanban.version import __version__

from FUTIL.my_logging import *

console_level = globals()[OKANBAN_CONSOLE_LEVEL]
logfile_level = globals()[OKANBAN_LOGFILE_LEVEL]
my_logging(console_level = console_level, logfile_level = logfile_level, details = True)

logging.info('OKanban API start')

app = Flask(__name__)
api = Api(app)

okanban_bdd = BddOKanbans(OKANBAN_MONGODB_HOST, OKANBAN_MONGODB_PORT)
okanban_printer = HttpNiceLabel(OKANBAN_NICELABEL_URL)
okanban_printer_name = None
#okanban_printer_name = "IMP_TEST"
okanban_etiquette = OKANBAN_ETIQUETTE

auth = HTTPBasicAuth()
users = {
    OKANBAN_API_USERNAME: generate_password_hash(OKANBAN_API_PASSWORD)
}
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

class OkanbanApihello(Resource):
    def get(self):
        return f"OKanban API is running. Version: {__version__}. OKANBAN_NICELABEL_URL: {OKANBAN_NICELABEL_URL}"

okanban_api_parser = reqparse.RequestParser()
okanban_api_parser.add_argument('proref', type=str, required = True)
okanban_api_parser.add_argument('qte', type=int)
okanban_api_parser.add_argument('date', type=str)
okanban_api_parser.add_argument('remarques', type=str)
okanban_api_parser.add_argument('conforme', type=str)
okanban_api_parser.add_argument('operateur', type=str)
okanban_api_parser.add_argument('mesures', type=dict)
okanban_api_parser.add_argument('only_print', type=bool)

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

    t_validation = {
        True : 'Vrai',
        False : 'Faux',
        None : ''
    }    
    
    @auth.login_required
    def post(self):
        '''Création d'un kanban
        args : {
            'proref': '7TDSIEGE',
            'qte': 99,
            'date': '07/03/2024',
            'remarques': '',
            'conforme': 'OK',
            'operateur': 'Frédéric Thomé',
            'mesures': {
                'P1': {'value': '7', 'result': 'Vrai', 'mini': '6', 'maxi': '12'},
                'P2': {'value': '7', 'result': 'Faux', 'mini': '6', 'maxi': '12'},...
        '''
        args = okanban_api_parser.parse_args()
        args['conforme']= "OK" if args.get('conforme')in ['-1', 'OK', 'True'] else "NOK"
        args['date'] = datetime.date.today().strftime("%d/%m/%Y")
        try: #For access 97
            args['mesures'] = {cote : {k : float(v.replace(',','.')) if v.replace(',','.').isnumeric() else v for k, v in mesure.items()} for cote, mesure in args.get('mesures',{}).items()}
        except AttributeError:
            args['mesures'] = {cote : {k : self.t_validation.get(v,'') if (v is None or type(v)==bool) else v for k, v in mesure.items()} for cote, mesure in args.get('mesures',{}).items()}
        if not args.get('only_print'):
            #Creation d'un kanban
            id = okanban_bdd.set_kanban(proref=args['proref'], qte=args.get('qte'), type = "creation", mesures=args.get('mesures'), conforme = args.get('conforme'), operateur=args.get('operateur'), remarques=args.get('remarques'))
        else:
            id = ""
        try:
            #Imprime une étiquette kanban
            args['id'] = id
            args['printer'] = okanban_printer_name or okanban_bdd.get_param('printer')
            args['date_creation'] = args['date']
            del args['date']
            try:
                dure_degazage = okanban_bdd.get_references(args['proref'])[0]['duree_degazage']
            except (KeyError, IndexError):
                dure_degazage = None
            if dure_degazage is not None:
                args['duree_degazage'] = dure_degazage
            args['qty'] = 1 # Nb d'étiquettes
            args['etiquette'] = okanban_etiquette
            args['mesures'] = "\n".join([f"{mesure['cote']} : {mesure['value']}"  for mesure in args['mesures'].values() if mesure['result']== 'Faux'])
            okanban_printer.print(**args)
        except Exception as e:
            logging.error(e)
            if id:
                okanban_bdd.delete_kanban(id)
            return f"Error on API OKanbans: {e}", 400
        else:
            logging.info(f"POST : Création kanban : {args}")
            return "OK", 200 #TODO : renvoyer Id (et le gérer dans access!!)

api.add_resource(OkanbanApi, "/okanban/qte/<proref>", "/okanban")
api.add_resource(OkanbanApihello, "/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=OKANBAN_PORT, debug=False)