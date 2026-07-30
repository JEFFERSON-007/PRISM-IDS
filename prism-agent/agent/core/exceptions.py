"""Custom Exceptions for PRISM Agent Daemon."""


class AgentBaseException(Exception):
    """Base exception class for all PRISM Agent errors."""

    def __init__(self, message: str, code: str = "AGENT_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class AgentConfigurationError(AgentBaseException):
    """Raised when agent configuration is invalid."""

    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message=message, code="CONFIG_ERROR")


class AgentAuthenticationError(AgentBaseException):
    """Raised when agent authentication or credential validation fails."""

    def __init__(self, message: str = "Agent authentication failed") -> None:
        super().__init__(message=message, code="AUTH_ERROR")


class AgentCommunicationError(AgentBaseException):
    """Raised when REST HTTP or WebSocket communication encounters errors."""

    def __init__(self, message: str = "Server communication failed") -> None:
        super().__init__(message=message, code="COMMUNICATION_ERROR")


class SystemCollectionError(AgentBaseException):
    """Raised when local hardware/OS metric collection fails."""

    def __init__(self, message: str = "Metric collection failed") -> None:
        super().__init__(message=message, code="METRIC_COLLECTION_ERROR")
