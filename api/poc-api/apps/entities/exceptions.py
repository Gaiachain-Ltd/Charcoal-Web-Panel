from rest_framework.exceptions import APIException


class PackageAlreadyExistException(APIException):
    status_code = 409
    default_detail = 'Package with such id or qr_code already exists.'
    default_code = 'package_already_exist'


class EntityAlreadyExistException(APIException):
    status_code = 409
    default_detail = 'Entity with such id already exists.'
    default_code = 'entity_already_exist'
