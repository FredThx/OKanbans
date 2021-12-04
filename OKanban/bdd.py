# coding: utf-8

import pymongo, datetime
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

    def __init__(self, host = 'localhost', port = 27017):
        decimal_codec = DecimalCodec()
        type_registry = TypeRegistry([decimal_codec])
        self.codec_options = CodecOptions(type_registry=type_registry)
        self.bdd = pymongo.MongoClient(host, port).OKanbans
        self.references = self.get_collection('references')
        self.kanbans = self.get_collection('kanbans')
        self.params = self.get_collection('params')

    def get_collection(self, table):
        return self.bdd.get_collection(table, codec_options=self.codec_options)
    
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
        if list(self.references.find(filter)):
            self.references.update_many(filter,{'$set' : data})
        else:
            self.references.insert_one(data)

    def del_reference(self, proref):
        '''Delete a reference
        '''
        self.references.delete_one({'proref' : proref})

    def get_references(self, proref = None):
        '''get the list of all references
        '''
        if proref:
            filter = {'proref' : proref}
        else:
            filter = {}
        return list(self.references.find(filter))
    
    def get_id(self):
        '''Get the next id
        '''
        filter = {'param' : self.param_last_id}
        result = list(self.params.find(filter))
        if result:
            id = result[0].get('value',0) + 1
            self.params.update_many(filter, {'$set': {'value' : id}})    
        else:
            id = 1
            self.params.insert_one({'param': self.param_last_id, 'value' : id})
        return id

    def set_kanban(self, id = None, proref = None, qte = None, date_creation = None):
        ''' Create or change a kanban
        '''
        if id is None:
            kanban ={}
            kanban['id'] = self.get_id()
            assert proref is not None, "proref is needed to create a new kanban."
            reference = list(self.get_references(proref))
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
            kanban = list(self.kanbans.find({'id' : id}))
            assert len(kanban)>0, "unknow id"
            assert len(kanban)==1, f"Oups, duplicate id found in kanbans: {kanban}"
            kanban = kanban[0]
            if proref:
                assert proref in [ref.get('proref') for ref in self.get_references()], f"{proref} not present in references."
                kanban['proref']=proref
            if qte is not None:
                kanban['qte'] = qte
            if date_creation:
                kanban['date_creation'] = date_creation
            self.kanbans.update_many({'id' : id}, {'$set' : kanban})
            #TODO : ajouter historique
            