class BorrowDomainService:

    @staticmethod
    def validate_can_borrow(
        active_borrow,
        book,
    ):
        if active_borrow:
            raise ValueError("Book already borrowed by this user")
        
        if not book.is_available:
            raise ValueError("Book not available")
