class ReturnDomainService:

    @staticmethod
    def validate_can_ruturn(borrow_record):
        if borrow_record is None:
            raise ValueError("Borrow record not found")
        
        if borrow_record.returned_at is not None:
            raise ValueError("Book already returned")
