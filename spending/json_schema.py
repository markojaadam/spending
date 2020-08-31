import time


class ValidationSchema(object):

    @property
    def ADD_SPENDING_SCHEMA(self):
        return {
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'properties': {
                'amount': {
                    'type': 'number',
                    'minimum': 0.01,
                    "multipleOf": 0.01
                },
                'currency': {
                    'type': 'string',
                    'minLength': 3,
                    'maxLength': 3
                },
                'reason': {
                    'type': ['string', 'null'],
                },
                'date': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': int(time.time()) + 1
                }
            },
            'required': [
                'amount',
                'currency',
                'reason',
                'date'
            ],
            "additionalProperties": False
        }

    @property
    def UPDATE_SPENDING_SCHEMA(self):
        return {
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'minimum': 1
                },
                'amount': {
                    'type': 'number',
                    'minimum': 0.01,
                    "multipleOf": 0.01
                },
                'currency': {
                    'type': 'string',
                    'minLength': 3,
                    'maxLength': 3
                },
                'reason': {
                    'type': ['string', 'null'],
                },
                'date': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': int(time.time()) + 1
                }
            },
            'required': [
                'id',
                'amount',
                'currency',
                'reason',
                'date'
            ],
            "additionalProperties": False
        }

    @property
    def DELETE_SPENDING_SCHEMA(self):
        return {
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'minimum': 1
                }
            },
            'required': [
                'id'
            ],
            "additionalProperties": False
        }
