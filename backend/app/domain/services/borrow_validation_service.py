class BorrowValidationService:

    @staticmethod
    def validate_user_exists(user):
        if not user:
            raise ValueError("User not found")
        
    @staticmethod
    def validate_book_exists(book):
        if not book:
            raise ValueError("Book not found")
