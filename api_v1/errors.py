from flask import jsonify

from api_v1.db_data_returns import Files

class FileErrors:

    @staticmethod
    def file_not_found(file_id: int):
        return jsonify({
            "message": f"File with id '{file_id}' not found!",
            "error": "FileNotFount",
            "code": 404
        }), 404

    @staticmethod
    def file_not_uploaded():
        return jsonify({
            "message": "File not uploaded!",
            "error": "FileNotUpload",
            "code": 400
        }), 400

    @staticmethod
    def file_not_selected():
        return jsonify({
            "message": "File not selected!",
            "error": "FileNotSelected",
            "code": 400
        }), 400

    @staticmethod
    def other_errors_with_file(e: all):
        return jsonify({
            "message": str(e),
            "error": type(str(e)),
            "code": 500
        }), 500


class BooksCatalogErrors:

    @staticmethod
    def book_not_found(book_id):
        return jsonify({
            "message": f"""Book with id = '{book_id}' not found!""",
            "error": "ResourceNotFound",
            "code": 404
        }), 404




EMAIL_ALREADY_EXISTS = {
    "error": "EmailAlreadyExists",
    "message": "The email address is already in use. Please try another one.",
    "code": 409
}
USERNAME_ALREADY_EXISTS = {
  "error": "UsernameAlreadyExists",
  "message": "The username is already taken. Please choose another one.",
  "code": 409
}
INVALID_PASSWORD = {
  "error": "InvalidPassword",
  "message": "The password does not meet the required criteria. It must include at least 8 characters, one uppercase letter, one number, and one special character.",
  "code": 404
}
FILE_NOT_FOUND = {
    "error": "FileNotFount",
    "message": "File not found!",
    "code": 404
}
NOT_PERMISSION = {
    "error": "Forbidden",
    "message": "No permission",
    "code": 403
}
BOOK_NOT_FOUND = {
    "error": "BookNotFound",
    "message": "Book not found",
    "code": 404
}