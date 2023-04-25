'''Une API pour OKanban

ca tourne sur : TODO

url : localhost:50889/okanban
'''
from flask import Flask, request
#from flask_cors import CORS
from flask_restful import abort, Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from bdd import BddOKanbans
from nicelabel import HttpNiceLabel

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
            abort(404, message=f"{proref} doesn't existe.")
        else:
            ref = ref[0]
            return ref.get('qte_kanban_plein')
        
    @auth.login_required
    def post(self):
        '''Création d'un kanban
        '''
        #args = request.get_json(force=True)
        args = okanban_api_parser.parse_args()
        args['conforme']=args.get('conforme')=='-1'
        # todo : trier les mesures P1, R1, ...
        args['mesures']= ', '.join([f"{cote}:{float(mesure.replace(',','.'))}" for cote, mesure in args.get('mesures',{}).items()])
        args['date'] = datetime.date.today().strftime("%d/%m/%Y")
        #Creation d'un kanban
        id = okanban_bdd.set_kanban(proref=args['proref'], qte=args.get('qte'), type = "creation")
        #Imprime une étiquette kanban
        args['id'] = 42
        args['printer'] = okanban_printer_name
        args['date_creation'] = args['date']
        del args['date']
        args['qty'] = 1 # Nb d'étiquettes
        args['etiquette'] = okanban_etiquette
        print(args)
        okanban_printer.print(**args)
        return "OK", 200

api.add_resource(OkanbanApi, "/okanban/qte/<proref>", "/okanban")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=50889, debug=False)