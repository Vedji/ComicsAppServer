from flask import jsonify, Blueprint, Response, request


class CustomException(Exception):
    def __init__(self, message: str, error="This error is not validation", status_code: int = 400, *args):
        self.message = message
        self.error = error
        self.status_code = status_code
        super().__init__(message, args)
        ", ".join([])

    def to_json(self) -> dict:
        return {
            "message": self.message,
            "code": self.status_code,
            "error": self.error
        }

    def response(self) -> (Response, int):
        return jsonify(self.to_json()), self.status_code


# Классы исключений для работы с API
class InvalidField(CustomException):
    """
    Исключение вызывается, когда передано неверное поле.

    :param field_name: Название неверного поля
    :param field_value: Значение неверного поля
    :param field_type: Ожидаемый тип поля
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 400)
    """
    def __init__(self, field_name: str, field_value: any, field_type: str, message: str = "Invalid field provided", status_code: int = 400):
        detailed_message = f"Invalid field: {field_name} (value: {field_value}, type: {type(field_value)}, expected: {field_type}). {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class NotFound(CustomException):
    """
    Исключение вызывается, когда запрашиваемый ресурс не найден.

    :param resource_name: Название отсутствующего ресурса
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 404)
    """

    def __init__(self, resource_name: str, message: str = "Resource not found", status_code: int = 404, **kwargs):
        resource_kwargs = ", ".join([f"{key} = {value}" for key, value in kwargs.items()])
        detailed_message = f"Not found resource: <{resource_name}({resource_kwargs})>. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class NotPermission(CustomException):
    """
    Исключение вызывается, когда действие запрещено из-за недостатка прав.

    :param action: Действие, которое пытаются выполнить
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 403)
    """
    def __init__(self, action: str, message: str = "Access denied", status_code: int = 403):
        detailed_message = f"Permission denied for action: {action}. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class ResourceHasExists(CustomException):
    """
    Исключение вызывается, когда пытаются создать ресурс, который уже существует.

    :param resource_name: Название существующего ресурса
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 409)
    """
    def __init__(self, resource_name: str, message: str = "Resource already exists", status_code: int = 409):
        detailed_message = f"Resource already exists: {resource_name}. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class DeleteError(CustomException):
    """
    Исключение вызывается при ошибке удаления ресурса.

    :param resource_name: Название удаляемого ресурса
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 500)
    """

    def __init__(self, resource_name: str, message: str = "Error during deletion", status_code: int = 500, **kwargs):
        resource_kwargs = ", ".join([f"{key} = {value}" for key, value in kwargs.items()])
        detailed_message = f"Error deleting resource: <{resource_name}({resource_kwargs})>. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class DataValidationError(CustomException):
    """
    Исключение вызывается при ошибке проверки данных.

    :param field_name: Название поля, не прошедшего проверку
    :param field_value: Неверное значение поля
    :param field_type: Ожидаемый тип поля
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 422)
    """
    def __init__(self, field_name: str, field_value: any, field_type: str, message: str = "Data validation error", status_code: int = 422):
        detailed_message = f"Data validation error for field: {field_name} (value: {field_value}, type: {type(field_value)}, expected: {field_type}). {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class ResourceTimeoutError(CustomException):
    """
    Исключение вызывается при превышении времени ожидания операции с ресурсом.

    :param resource_name: Название ресурса, для которого произошло превышение времени
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 504)
    """
    def __init__(self, resource_name: str, message: str = "Resource timeout", status_code: int = 504):
        detailed_message = f"Resource timeout for: {resource_name}. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class UpdateError(CustomException):
    """
    Исключение вызывается при ошибке обновления ресурса.

    :param resource_name: Название ресурса, который не удалось обновить
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 500)
    :param **kwargs: Параметры обновляемого ресурса
    """
    def __init__(self, resource_name: str, message: str = "Error during update", status_code: int = 500, **kwargs):
        resource_kwargs = ", ".join([f"{key} = {value}" for key, value in kwargs.items()])
        detailed_message = f"Error updating resource: <{resource_name}({resource_kwargs})>. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class FetchError(CustomException):
    """
    Исключение вызывается при ошибке получения данных из API.

    :param resource_name: Название ресурса, который не удалось получить
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 500)
    """
    def __init__(self, resource_name: str, message: str = "Error during fetch", status_code: int = 500):
        detailed_message = f"Error fetching resource: {resource_name}. {message}"
        error = self.__class__.__name__
        super().__init__(detailed_message, error=error, status_code=status_code)


class AuthorizationError(CustomException):
    """
    Исключение вызывается, когда пользователь не авторизован для выполнения действия.

    :param action: Действие, которое пользователь не может выполнить
    :param message: Дополнительное сообщение об ошибке (опционально)
    :param status_code: HTTP-код статуса (по умолчанию: 401)
    """
    def __init__(self, action: str, message: str = "User is not authorized to perform this action", status_code: int = 401):
        detailed_message = f"Authorization failed for action: {action}. {message}"
        error = self.__class__.__name__
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
        return e.response()

    @blueprint.errorhandler(InvalidField)
    def handle_invalid_field_error(error: InvalidField):
        return error.response()

    @blueprint.errorhandler(NotFound)
    def handle_not_found_error(error: NotFound):
        return error.response()

    @blueprint.errorhandler(NotPermission)
    def handle_not_permission_error(error: NotPermission):
        return error.response()

    @blueprint.errorhandler(ResourceHasExists)
    def handle_resource_has_exists_error(error: ResourceHasExists):
        return error.response()

    @blueprint.errorhandler(DeleteError)
    def handle_delete_error(error: DeleteError):
        return error.response()

    @blueprint.errorhandler(DataValidationError)
    def handle_data_validation_error(error: DataValidationError):
        return error.response()

    @blueprint.errorhandler(ResourceTimeoutError)
    def handle_resource_timeout_error(error: ResourceTimeoutError):
        return error.response()

    @blueprint.errorhandler(UpdateError)
    def handle_update_error(error: UpdateError):
        return error.response()

    @blueprint.errorhandler(FetchError)
    def handle_fetch_error(error: FetchError):
        return error.response()

    @blueprint.errorhandler(AuthorizationError)
    def handle_invalid_field_error(error: AuthorizationError) -> Response:
        return error.response()


if __name__ == '__main__':
    try:
        raise UpdateError("comment", "", 500, test = "T1", lost = "Lost a1", large = 123)
    except CustomException as e:
        print(e.to_json())