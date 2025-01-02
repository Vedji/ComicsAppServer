from flask import jsonify


class ExtensionsReturned:

    @staticmethod
    def invalid_field(field_name: str, field_value: str):
        return jsonify({
            "message": f"Field {field_name} = '{field_value}' is incorrect, type = {type(field_value)}",
            "code": 401,
            "error": "InvalidValue"
        }), 401

    @staticmethod
    def not_found(not_found_field: str, not_found_value):
        return jsonify({
            "message": f"Resource {not_found_field} with id = '{not_found_value}' not found!",
            "error": "ResourceNotFound",
            "code": 404
        }), 404

    @staticmethod
    def upload_error(upload_obj: str, obj: int):
        return jsonify({
            "message": f"Upload object {upload_obj}? with id = '{obj.__str__()}'.",
            "error": "UploadError",
            "code": 400
        }), 400

    @staticmethod
    def not_permission(user_id: int, permission: int):
        return jsonify({
            "message": f"User with id = '{user_id}', permission = '{permission}' has not access.",
            "error": "AccessDenied",
            "code": 403
        }), 403

    @staticmethod
    def resource_has_exists(obj: str):
        return jsonify({
            "message": f"Record {obj} already exists!",
            "error": "RecordAlreadyExists",
            "code": 409
        }), 409

    @staticmethod
    def delete_error(obj: str):
        return jsonify({
            "message": f"Object {obj} has not deleted!",
            "error": "DeleteError",
            "code": 404
        }), 404