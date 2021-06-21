import functools
#from http import HTTPStatus

from ..exceptions.entity_not_found import EntityNotFound
from ..exceptions.not_allowed import NotAllowed

def handle():
    def decorator(function):
        @functools.wraps(function)
        def wrapper(self, *args):
            try:
                result = function(self, *args)
                self.write_response(
                    status_code=200, result=result)
            except EntityNotFound:
                self.write_error(status_code=400,
                                 message="entity not found")
            except NotAllowed:
                self.write_error(status_code=403,
                                 message="forbidden")
            except Exception as err:
                self.write_error(status_code=500,
                                 message=str(err))

        return wrapper

    return decorator


