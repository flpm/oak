def merge_books(catalogue, books):
    new_books = 0
    for book_id, book_info in books.items():
        for book_type, book in book_info.items():
            if book_id in catalogue:
                if book_type in catalogue[book_id]:
                    current_book = catalogue[book_id][book_type]
                    for key, value in book.items():
                        current_book[key] = value
                else:
                    catalogue[book_id][book_type] = book
            else:
                catalogue[book_id][book_type] = book
                new_books += 1
    return catalogue, new_books
