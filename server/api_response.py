import flask


class ApiResponse:

    def __init__(self, data: (dict, list, str, int, float, type(None)), metadata: dict = None, status: str = "success"):
        """
        Этот класс используется для структурирования и проверки ответов в едином формате.
        Он обеспечивает соответствие атрибутов `status`, `data` и необязательного `metadata`
        определённым типам и структурам,
        а также предоставляет метод для преобразования ответа в формат, совместимый с JSON.

        :param status: Статус ответа (например: "success", "error")
        :type status: str
        :param data: Данные ответа (любой из представленных ниже)
        :type data: (dict, list, str, int, float, or None)
        :param metadata: Дополнительная информация. По умолчанию пустой словарь
        :type metadata: (dict, optional)

        """

        if not isinstance(status, str):
            raise ValueError("Status must be a string")
        if not isinstance(data, (dict, list, str, int, float, type(None))):
            raise TypeError("Data must be of a valid type (dict, list, str, int, float, or None)")
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("Metadata must be a dictionary")

        self.status = status
        self.data = data
        self.metadata = metadata

    def to_json(self):
        response = {
            "status": self.status,
            "data": self.data
        }
        if self.metadata:
            response["metadata"] = self.metadata
        return response

    def response(self, code: int = 200):
        return flask.jsonify(self.to_json()), code


if __name__ == "__main__":
    response_array = ApiResponse(
        status="success",
        data=[1, 2, 3, 4, 5]
    )
    print(response_array.to_json())

    response_dict = ApiResponse(
        status="success",
        data={"key1": "value1", "key2": "value2"}
    )
    print(response_dict.to_json())

    response_paginated = ApiResponse(
        status="success",
        data=
        [
            {"id": 21, "name": "Item 21"},
            {"id": 22, "name": "Item 22"}
        ],
        # Метаданные, связанные с пагинацией, для удобства навигации по большому набору данных
        metadata={
            "total": 500,  # Общее количество доступных элементов в наборе данных
            "offset": 20,  # Текущее смещение — с какого элемента начинается текущая страница
            "limit": 10,  # Количество элементов на одной странице (размер страницы)

            # Флаг, указывающий, есть ли данные на следующей странице
            "hasNext": True,

            # Флаг, указывающий, есть ли данные на предыдущей странице
            "hasPrevious": True,

            # Логический номер текущей страницы, рассчитываемый как (offset // limit if limit > 0 else 0)
            "currentPage": 3,

            # Общее количество страниц в наборе данных, рассчитываемое как (total / limit)
            "totalPages": 50,
        }
    )
    print(response_paginated.to_json())
