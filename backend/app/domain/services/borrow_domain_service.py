class BorrowDomainService:

    @staticmethod
    def validate_can_borrow(
        active_borrow,
        available_copies: int,
    ):
        if active_borrow:
            raise ValueError("User has already borrowed this book")
        
        if available_copies <= 0:
            raise ValueError("No available copies left")
