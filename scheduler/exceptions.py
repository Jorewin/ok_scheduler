class FileContentError(Exception):
    """Called if the contents of the file don't meet the specified requirements."""


class IncorrectGeneratorDatasetError(Exception):
    """Exception that is called if input parameters to generator are incorrect."""
