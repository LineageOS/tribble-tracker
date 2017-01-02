from datetime import datetime, timedelta

from mongoengine import Document, EmbeddedDocument
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField, ListField, IntField

class Statistic(Document):
    d = StringField(required=True)          #device_id
    m = StringField(required=True)          #model
    v = StringField(required=True)          #version
    u = StringField(required=True)          #country
    c = StringField(required=True)          #carrier
    c_id = StringField(required=True)       #carrier_id
    t = DateTimeField(default=datetime.now) #submit_time

    meta = { "indexes": ["m", "u"] }

    @classmethod
    def get_most_popular(cls, field, days):
        res = Statistic.objects().aggregate({ '$match': { 't': { '$gte': datetime.now()-timedelta(days=days) } } }, { '$group': { '_id': '$' + cls.field_map[field], 'total': { '$sum': 1 } }}, {'$sort': {'total': -1} })
        return list(res)

    @classmethod
    def get_count(cls, days=90):
        res = cls.objects(t__gte=datetime.now()-timedelta(days=days)).count()
        return res

    @classmethod
    def get_stats_from(cls, days=90):
        return cls.objects(t__gte=datetime.now()-timedelta(days=days))

    field_map = {
        'device_id': 'd',
        'model': 'm',
        'version': 'v',
        'country': 'u',
        'carrier': 'c',
        'carrier_id': 'c_id',
        'submit_time': 't'
    }

class PoorlyNamedEmbeddedDocument(EmbeddedDocument): # working title
    v = StringField(required=True) # value
    c = IntField(required=True) # count

    def __str__(self):
        return str(self.v) + " " + str(self.c)

    field_map = {
        'value': 'v',
        'count': 'c'
    }

class FieldAggregates(Document):
    d = DateTimeField(required=True)    # date
    f = StringField(required=True)      # field_name
    v = ListField(EmbeddedDocumentField(PoorlyNamedEmbeddedDocument, required=True)) # values

    field_map = {
        'date': 'd',
        'field_name': 'f',
        'values': 'v'
    }
