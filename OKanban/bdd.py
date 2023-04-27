# coding: utf-8

import pymongo, datetime, logging, time, socket
from bson.decimal128 import Decimal128
from bson.codec_options import TypeCodec
from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions
from decimal import Decimal

class DecimalCodec(TypeCodec):
    python_type = Decimal    # the Python type acted upon by this type codec
    bson_type = Decimal128   # the BSON type acted upon by this type codec
    def transform_python(self, value):
        """Function that transforms a custom type value into a type
        that BSON can encode."""
        return Decimal128(value)
    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        return value.to_decimal()

class BddOKanbans(object):
    ''' La base de donnée mongoDB où sont stockés les données
    '''
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    param_last_id = 'last_id'

    def __init__(self, host = 'localhost', port = 27017, cache_timeout = 60):
        ''' host    :   mongodb serveur
            port    :   mondodb port
            cache_timeout   :   duration (seconds) for keeping data on cache
        '''
        decimal_codec = DecimalCodec()
        type_registry = TypeRegistry([decimal_codec])
        self.codec_options = CodecOptions(type_registry=type_registry)
        self.bdd = pymongo.MongoClient(host, port).OKanbans
        self.references = self.get_collection('references')
        self.kanbans = self.get_collection('kanbans')
        self.params = self.get_collection('params')
        self.instances = self.get_collection('instances')
        self.cache_references = None
        self.cache_references_timeout = None
        self.cache_kanbans = None
        self.cache_kanbans_timeout = None
        self.cache_timeout = cache_timeout

    def cache_clear(self):
        '''Clear all caches : references, kanbans
        '''
        self.cache_references = None
        self.cache_kanbans = None

    def get_collection(self, table):
        return self.bdd.get_collection(table, codec_options=self.codec_options)

    def get_list(self, cursor):
        '''Execute the query and return a list of results
        '''
        try:
            return list(cursor)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.warning(e)
            return []

    @staticmethod
    def date_to_str(date, time = False):
        if isinstance(date, datetime.date):
            date = date.isoformat()
            if not time:
                date = date.split('T')[0]
        return date

    def set_reference(self, proref, qte_kanban_plein = 100, nb_max = 0, nb_alerte = 0):
        ''' Crée ou modifie une référence
        '''
        data = locals().copy()
        filter = {'proref' : proref}
        del data['self']
        if self.get_list(self.references.find(filter)):
            self.references.update_many(filter,{'$set' : data})
        else:
            self.references.insert_one(data)
        self.cache_references = None
        self.send_message_new(proref)#même quand rien n'est changé!

    def del_reference(self, proref):
        '''Delete a reference
        '''
        #TODO : vérifier si kanbans non vides existes
        self.references.delete_one({'proref' : proref})
        self.cache_references = None
        self.send_message_new(proref)

    def get_references(self, proref = None):
        '''get the list of all references
        (avec systeme cache)
        '''
        if not(self.cache_references and self.cache_references_timeout and self.cache_references_timeout > time.time()):
            self.cache_references = self.get_list(self.references.find())
            self.cache_references_timeout = time.time() + self.cache_timeout
        if proref:
            return [ref for ref in self.cache_references if ref.get('proref')==proref]
        else:
            return self.cache_references

    def get_params(self, param=None):
        '''Get [one] or all params
        '''
        if param:
            filter = {'param' : param}
        else:
            filter = {}
        return self.get_list(self.params.find(filter))

    def set_params(self,param, value):
        '''Save param / value on bdd
        '''
        filter = {'param' : param}
        if self.get_params(param):
            self.params.update_many(filter, {'$set': {'value' : value}})
        else:
            self.params.insert_one({'param': self.param_last_id, 'value' : value})

    def del_param(self, param):
        '''Delete a parameter
        '''
        result = self.params.delete_one({'param' : param})
        logging.debug(f"Delete parameter {param} : {result.raw_result}")
        self.cache_params = None

    def get_id(self):
        '''Get the next id
        '''
        result = self.get_params(self.param_last_id)
        if result:
            id = int(result[0].get('value',0)) + 1
        else:
            id = 1
        self.set_params(self.param_last_id, id)
        return id

    def set_kanban(self, id = None, proref = None, qte = None, date_creation = None, type = None, mesures = None):
        ''' Create or change a kanban
        mesures : mesures du perçage
        '''
        if id is None:
            kanban ={'triggered' : False}
            kanban['id'] = self.get_id()
            assert proref is not None, "proref is needed to create a new kanban."
            reference = self.get_list(self.get_references(proref))
            assert len(reference)>0, "proref must exist to create a new kanban"
            assert len(reference)==1, f"Oups, duplicate proref in references : {reference}"
            kanban['proref'] = proref
            reference = reference[0]
            if qte is None:
                qte = reference.get('qte_kanban_plein')
            kanban['qte'] = qte
            if date_creation is None:
                date_creation = datetime.datetime.now()
            kanban['date_creation'] = date_creation
            mvt = {
                    'date' : date_creation,
                    'type' : type or 'creation',
                    'qte' : qte,
                    'hostname' : socket.gethostname(),
                    'triggered' : False
                    }
            kanban['mvts'] = [mvt]
            kanban['mesures'] = mesures
            self.kanbans.insert_one(kanban)
        else:
            kanban = self.get_list(self.kanbans.find({'id' : id}))
            assert len(kanban)>0, "unknow id"
            assert len(kanban)==1, f"Oups, duplicate id found in kanbans: {kanban}"
            kanban = kanban[0]
            qte0 = kanban['qte']
            if proref:
                assert proref in [ref.get('proref') for ref in self.get_references()], f"{proref} not present in references."
                kanban['proref']=proref
            if qte is not None:
                kanban['qte'] = int(qte)
            if date_creation:
                kanban['date_creation'] = date_creation
            mvt = {
                'date' : date_creation or datetime.datetime.now(),
                'type' : type or ('production' if qte>qte0 else 'consommation'),
                'qte' : qte - qte0,
                'hostname' : socket.gethostname(),
                'triggered' : False
                }
            kanban['mvts'] = (kanban.get('mvts') or [])+[mvt]
            kanban['triggered'] : False
            self.kanbans.update_many({'id' : id}, {'$set' : kanban})
        self.cache_kanbans = None
        self.send_message_new(kanban['id'])
        return kanban['id']

    def set_kanban_triggered(self, kanban):
        self.kanbans.update_many({'id' : kanban['id']}, {'$set' : kanban})
        #On pourrait aussi utiliser '_id': ObjectId('63be737b29396473e1c6125f')

    def get_kanbans(self, id=None, proref = None, all = False, only_not_triggered = False):
        '''Renvoie la liste des kanbans (limité à 1 éventuellement ou proref)
        (avec systeme cache)
        all     :   si False ou omis : uniquement les kanbans non vides
                    si True : tous les kanbans (pas de cache)
        only_not_triggered : si True : uniquement les kanbans non triggered (pas de cache)
        '''
        if all:
            return self.get_list(self.kanbans.find())
        elif only_not_triggered:
            filter = {'triggered' : False}
            return self.get_list(self.kanbans.find(filter))
        else:
            filter={'qte' : {'$gt' : 0}}
            if not(self.cache_kanbans and self.cache_kanbans_timeout and self.cache_kanbans_timeout > time.time()):
                self.cache_kanbans = self.get_list(self.kanbans.find(filter))
                self.cache_kanbans_timeout = time.time() + self.cache_timeout
            if id:
                return [k for k in self.cache_kanbans if k.get('id')==id]
            elif proref:
                return [k for k in self.cache_kanbans if k.get('proref')==proref]
            else:
                return self.cache_kanbans

    def send_message_new(self, id):
        '''Envoie à toutes les instances de l'application la notification qu'un kanban a été créé
        '''
        for instance in self.get_actives_apps():
            news = instance['news'] + [id]
            self.instances.update_one({'id' : instance['id']},{'$set' : {'news' : news}})
            logging.debug(f"Add new for instance {instance['id']} : {id}. news = {news}")

    def send_message_drop(self, id):
        '''Envoie à toutes les instances de l'application la notification qu'un kanban a été supprimé
        '''
        for instance in self.get_actives_apps():
            news = instance['drops'] + [id]
            self.instances.update_one({'id' : instance['id']},{'$set': {'drops' : news}})

    def get_actives_apps(self):
        '''Renvoie un cursor des instances de l'application actives
        '''
        return self.instances.find()

    def create_new_instance(self):
        '''Create a new instance de l'application
        and return the new id
        '''
        id = time.time()
        self.instances.insert_one({'id': id, 'news' :[], 'drops' : []})
        logging.info(f"New instance in bdd : id={id}")
        return id

    def delete_instance(self, id):
        '''Delete the instance
        '''
        result = self.instances.delete_one({'id' : id})
        logging.info(f"Delete instance in bdd : {result.raw_result}")
        return result

    def get_messages(self, id):
        '''Renvoie un tuple avec ([news, ], [drops, ])
        '''
        instance = self.instances.find_one({'id' : id})
        if instance:
            news, drops = instance.get('news'), instance.get('drops')
            self.instances.update_one({'id' : instance['id']},{'$set': {'news' : [], 'drops' : []}})
            return news, drops

    def clean_instances(self, my_id=None, timeout = 10):
        '''Delete not actives instances.
        '''
        logging.info("Clean instances...")
        self.send_message_new('_')
        time.sleep(timeout)
        for instance in self.get_actives_apps():
            if instance.get('id') != my_id and '_' in instance.get('news',[]):
                self.delete_instance(instance.get('id'))
        logging.info("... Clean instances end")
