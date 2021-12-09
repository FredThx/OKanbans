# coding: utf-8

import pymongo, datetime, logging, time
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

    def del_reference(self, proref):
        '''Delete a reference
        '''
        #TODO : vérifier si kanbans non vides existes
        self.references.delete_one({'proref' : proref})
        self.cache_references = None

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

    def get_id(self):
        '''Get the next id
        '''
        result = self.get_params(self.param_last_id)
        if result:
            id = result[0].get('value',0) + 1
        else:
            id = 1
        self.set_params(self.param_last_id, id)
        return id

    def set_kanban(self, id = None, proref = None, qte = None, date_creation = None):
        ''' Create or change a kanban
        '''
        if id is None:
            kanban ={}
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
            self.kanbans.insert_one(kanban)            
        else:
            kanban = self.get_list(self.kanbans.find({'id' : id}))
            assert len(kanban)>0, "unknow id"
            assert len(kanban)==1, f"Oups, duplicate id found in kanbans: {kanban}"
            kanban = kanban[0]
            if proref:
                assert proref in [ref.get('proref') for ref in self.get_references()], f"{proref} not present in references."
                kanban['proref']=proref
            if qte is not None:
                kanban['qte'] = int(qte)
            if date_creation:
                kanban['date_creation'] = date_creation
            self.kanbans.update_many({'id' : id}, {'$set' : kanban})
            #TODO : ajouter historique
        self.cache_kanbans = None
    
    def get_kanbans(self, id=None, proref = None, all = False):
        '''Renvoie la liste des kanbans (limité à 1 éventuellement ou proref)
        (avec systeme cache)
        all     :   si False ou omis : uniquement les kanbans non vides
                    si True : tous les kanbans (pas de cache)
        '''
        if all:
            return self.get_list(self.kanbans.find())
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
            self.instances.update_one({'_id' : instance['id']},{'news' : news})

    
    def send_message_drop(self, id):
        '''Envoie à toutes les instances de l'application la notification qu'un kanban a été supprimé
        '''
        for instance in self.get_actives_apps():
            news = instance['drops'] + [id]
            self.instances.update_one({'_id' : instance['id']},{'drops' : news})

    def get_actives_apps(self):
        '''Renvoie un cursor des instances de l'application actives
        '''
        return self.instances.find()
    
    def create_new_instance(self):
        '''Create a new instance de l'application
        and return the new id
        '''
        id = time.time()
        self.instancse.insert_one({'id': id, 'news' :[], 'drops' : []})    
        return id

    def get_modifications(self, id):
        '''Renvoie un tuple avec ([news, ], [drops, ])
        '''
        instance = self.instances.find_one({'id' : id})
        if instance:
            return instance.get('news'), instance.get('drops')
