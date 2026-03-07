class PipelineError(Exception):
    """Base exception for pipeline errors"""

    pass


class ValidationError(PipelineError):
    """Raised when input validation fails"""

    pass


class ProcessingError(PipelineError):
    """Raised when processing fails"""

    pass


class SafelyIgnoreableError(PipelineError):
    """Raised when processing fails but should be ignored"""

    pass
