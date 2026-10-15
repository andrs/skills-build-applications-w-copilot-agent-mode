class ServiceError(Exception):
    """Base class for all service-layer exceptions."""


class NotFoundError(ServiceError):
    def __init__(self, resource: str, id: int | str) -> None:
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id '{id}' not found")


class DuplicateResourceError(ServiceError):
    def __init__(self, resource: str, field: str, value: str) -> None:
        self.resource = resource
        self.field = field
        self.value = value
        super().__init__(f"{resource} with {field}='{value}' already exists")


class InvalidOperationError(ServiceError):
    """Raised when a business rule or lifecycle constraint is violated."""
