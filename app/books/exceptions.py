class BookError(Exception):
	"""Base class for all book-related exceptions."""

	pass


class BookNotFoundError(BookError):
	"""Exception raised when a book is not found."""

	def __init__(self, book_id: int):
		self.book_id = book_id
		super().__init__(f"Book with id {book_id} not found.")
