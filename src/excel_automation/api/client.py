"""Consumo de APIs externas via requisições HTTP (requests)."""

import logging
from typing import Any

import requests
from requests import Response, Session
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class APIClient:
    """Cliente HTTP para consumo de APIs externas.

    Utiliza uma :class:`requests.Session` para reaproveitar conexões.
    """

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        """Inicializa o cliente.

        Args:
            base_url: URL base da API (ex.: ``https://api.example.com``).
            timeout: Timeout em segundos para cada requisição.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: Session = requests.Session()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Realiza uma requisição GET e retorna o corpo como JSON.

        Args:
            path: Caminho relativo ao ``base_url`` (ex.: ``/v1/data``).
            params: Parâmetros de query string opcionais.

        Returns:
            Objeto Python desserializado do JSON de resposta.

        Raises:
            requests.HTTPError: Se o servidor retornar status de erro (4xx/5xx).
            requests.RequestException: Em caso de erro de rede ou timeout.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.info("GET %s params=%s", url, params)
        try:
            response: Response = self._session.get(
                url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            logger.error("Erro na requisição GET %s: %s", url, exc)
            raise

    def post(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        """Realiza uma requisição POST com corpo JSON.

        Args:
            path: Caminho relativo ao ``base_url``.
            payload: Dicionário a ser serializado como JSON no corpo.

        Returns:
            Objeto Python desserializado do JSON de resposta.

        Raises:
            requests.HTTPError: Se o servidor retornar status de erro (4xx/5xx).
            requests.RequestException: Em caso de erro de rede ou timeout.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.info("POST %s", url)
        try:
            response: Response = self._session.post(
                url, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            logger.error("Erro na requisição POST %s: %s", url, exc)
            raise

    def close(self) -> None:
        """Fecha a sessão HTTP subjacente."""
        self._session.close()

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
