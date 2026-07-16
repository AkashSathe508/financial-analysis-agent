class ServiceError(Exception):
    status_code = 500
    error_code = "service_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MissingPDFError(ServiceError):
    status_code = 400
    error_code = "missing_pdf"


class InvalidPDFError(ServiceError):
    status_code = 400
    error_code = "invalid_pdf"


class CorruptedPDFError(ServiceError):
    status_code = 400
    error_code = "corrupted_pdf"


class EmbeddingFailureError(ServiceError):
    status_code = 502
    error_code = "embedding_failure"


class VectorCreationError(ServiceError):
    status_code = 500
    error_code = "vector_creation_failure"


class NoProcessedDocumentError(ServiceError):
    status_code = 409
    error_code = "no_processed_document"


class GraphExecutionError(ServiceError):
    status_code = 502
    error_code = "graph_failure"


class ReportNotFoundError(ServiceError):
    status_code = 404
    error_code = "report_not_found"


class InvalidSessionError(ServiceError):
    status_code = 400
    error_code = "invalid_session"
