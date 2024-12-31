

class Books:

    @staticmethod
    def get_book(
            book_id: int,
            book_added_by: int,
            book_title: str,
            book_title_image: int,
            book_author: str,
            book_date_of_publication: str,
            book_rating: int,
            book_genres: list[str],
            book_description: str,
            book_isbn: str,
            book_added_at: str
    ) -> dict:
        return {
            "bookID": book_id,
            "bookAddedBy": book_added_by,
            "imagePreviewID": book_title_image,
            "bookTitle": book_title,
            "bookAuthor": book_author,
            "bookDateOfPublication": book_date_of_publication,
            "bookRating": book_rating,
            "bookGenres": book_genres,
            "bookDescription": book_description,
            "bookISBN": book_isbn,
            "bookAddedAt": book_added_at
        }

    @staticmethod
    def get_catalog_book(
            book_list: list[dict],
            page: int,
            count: int
    ):
        return {
            "booksList": book_list,
            "page": page,
            "count": count
        }


class Genres:

    @staticmethod
    def get_genre(
            genre_id: int,
            genre_name: str
    ):
        return {
            "genreID": genre_id,
            "genreName": genre_name
        }



class Files:
    DEFAULT_PATH = 'C:/Users/stret/PycharmProjects/ComicsApp/pythonProject1/data/'
    DEFAULT_FILE_PATH = '_default/'
    DEFAULT_FILE_TYPE = 'image/jpeg'
    DEFAULT_FILE_NAME = 'file_not_found.jpg'

    @staticmethod
    def get_file_info(
            file_id: int,
            added_by: int,
            file_name: str,
            file_type: str,
            upload_date: str,
            file_path: str
    ):
        return {
            "fileID": file_id,
            "addedBy": added_by,
            "fileName": file_name,
            "fileType": file_type,
            "uploadDate": upload_date,
            "filePath": file_path,
            "fileDirectory": Files.DEFAULT_PATH + file_path + file_name
        }
