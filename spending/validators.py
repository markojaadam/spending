from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
import jsonschema

class JSONSchemaValidator(BaseValidator):
    def validate(self, a):
        try:
            jsonschema.validate(a, self.limit_value)
        except jsonschema.exceptions.ValidationError as e:
            errmsg = str(e).split('\n')[0]
            raise ValidationError(errmsg)