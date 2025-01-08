from flask import jsonify, Blueprint, Response, request

from server.api_response import ApiResponse


class CustomException(Exception):
    def __init__(self, message: str, error="Error", status_code: int = 400, *args):
        self.message = message
        self.error = error
        self.status_code = status_code
        super().__init__(message, args)

    def to_response(self):
        data = {
            "message": self.message,
            "typeError": self.error,
            "statusCode": self.status_code
        }
        api_response = ApiResponse(data=data, status="error")
        return api_response.to_response(self.status_code)


class InvalidField(CustomException):
    def __init__(self, field_name: str, field_value: any, field_type: str, message: str = "Invalid field provided", status_code: int = 400):
        detailed_message = f"Invalid field: {field_name} (value: {field_value}, type: {type(field_value).__name__}, expected: {field_type}). {message}"
        error = "InvalidFieldError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class NotFound(CustomException):
    def __init__(self, resource_name: str, resource_id: any = None, message: str = "Resource not found", status_code: int = 404):
        resource_info = f" (ID: {resource_id})" if resource_id else ""
        detailed_message = f"Resource not found: {resource_name}{resource_info}. {message}"
        error = "NotFoundError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class NotPermission(CustomException):
    def __init__(self, action: str, message: str = "Access denied", status_code: int = 403):
        detailed_message = f"Permission denied for action: {action}. {message}"
        error = "PermissionDeniedError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class ResourceHasExists(CustomException):
    def __init__(self, resource_name: str, message: str = "Resource already exists", status_code: int = 409):
        detailed_message = f"Resource already exists: {resource_name}. {message}"
        error = "ResourceExistsError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class DeleteError(CustomException):
    def __init__(self, resource_name: str, resource_id: any = None, message: str = "Error during deletion", status_code: int = 500):
        resource_info = f" (ID: {resource_id})" if resource_id else ""
        detailed_message = f"Error deleting resource: {resource_name}{resource_info}. {message}"
        error = "DeleteError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class DataValidationError(CustomException):
    def __init__(self, field_name: str, field_value: any, field_type: str, message: str = "Data validation error", status_code: int = 422):
        detailed_message = f"Data validation error for field: {field_name} (value: {field_value}, type: {type(field_value).__name__}, expected: {field_type}). {message}"
        error = "DataValidationError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class ResourceTimeoutError(CustomException):
    def __init__(self, resource_name: str, message: str = "Resource timeout", status_code: int = 504):
        detailed_message = f"Timeout while accessing resource: {resource_name}. {message}"
        error = "ResourceTimeoutError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class UpdateError(CustomException):
    def __init__(self, resource_name: str, resource_id: any = None, message: str = "Error during update", status_code: int = 500):
        resource_info = f" (ID: {resource_id})" if resource_id else ""
        detailed_message = f"Error updating resource: {resource_name}{resource_info}. {message}"
        error = "UpdateError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class FetchError(CustomException):
    def __init__(self, resource_name: str, message: str = "Error during fetch", status_code: int = 500):
        detailed_message = f"Error fetching resource: {resource_name}. {message}"
        error = "FetchError"
        super().__init__(detailed_message, error=error, status_code=status_code)


class AuthorizationError(CustomException):
    def __init__(self, action: str, message: str = "User is not authorized to perform this action", status_code: int = 401):
        detailed_message = f"Authorization failed for action: {action}. {message}"
        error = "AuthorizationError"
        super().__init__(detailed_message, error=error, status_code=status_code)




def register_error_handlers(blueprint: Blueprint):
    """
    Регистрация обработчиков ошибок для Blueprint.

    :param blueprint: Экземпляр Blueprint, для которого регистрируются обработчики ошибок
    """
    print(f"register_error_handlers = {blueprint}")

    @blueprint.errorhandler(Exception)
    def handle_error(error: Exception):
        code = 404
        if "code" in dir(error):
            code = error.__getattribute__("code")
        error_url = request.url  # Получаем URL, где произошла ошибка
        request_method = request.method

        e = CustomException(
            str(error),
            f"Error in {blueprint} -> {type(error)}: {error.__repr__()} at {error_url} [Method: {request_method}]",
            code
        )
        return e.to_response()

    @blueprint.errorhandler(InvalidField)
    def handle_invalid_field_error(error: InvalidField):
        return error.to_response()

    @blueprint.errorhandler(NotFound)
    def handle_not_found_error(error: NotFound):
        return error.to_response()

    @blueprint.errorhandler(NotPermission)
    def handle_not_permission_error(error: NotPermission):
        return error.to_response()

    @blueprint.errorhandler(ResourceHasExists)
    def handle_resource_has_exists_error(error: ResourceHasExists):
        return error.to_response()

    @blueprint.errorhandler(DeleteError)
    def handle_delete_error(error: DeleteError):
        return error.to_response()

    @blueprint.errorhandler(DataValidationError)
    def handle_data_validation_error(error: DataValidationError):
        return error.to_response()

    @blueprint.errorhandler(ResourceTimeoutError)
    def handle_resource_timeout_error(error: ResourceTimeoutError):
        return error.to_response()

    @blueprint.errorhandler(UpdateError)
    def handle_update_error(error: UpdateError):
        return error.to_response()

    @blueprint.errorhandler(FetchError)
    def handle_fetch_error(error: FetchError):
        return error.to_response()

    @blueprint.errorhandler(AuthorizationError)
    def handle_invalid_field_error(error: AuthorizationError) -> Response:
        return error.to_response()


if __name__ == '__main__':
    try:
        raise UpdateError("comment", "", 500, test = "T1", lost = "Lost a1", large = 123)
    except CustomException as e:
        print(e.to_json())