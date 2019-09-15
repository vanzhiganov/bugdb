from functools import wraps
import jsonschema
from flask import request, current_app


def check_schema(schema):
    def validation(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # check content type
            if not request.headers.get('content-type') == 'application/json':
                return {}, 400
            try:
                jsonschema.validate(request.json, schema)
            except jsonschema.exceptions.ValidationError as error:
                current_app.logger.error(error)
                return {}, 400

            return func(*args, **kwargs)
        return decorated_function
    return validation
