#!/usr/bin/env python3
"""USPTO Open Data Portal API client for patent search and retrieval"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class PatentSearchResult:
    """Represents a patent search result from USPTO API"""

    application_number: str
    patent_number: Optional[str]
    filing_date: Optional[str]
    grant_date: Optional[str]
    title: Optional[str]
    application_type: Optional[str]
    status: Optional[str]
    inventors: List[str]
    applicants: List[str]
    abstract: Optional[str]
    raw_data: Dict[str, Any]


class USPTOAPIError(Exception):
    """Base exception for USPTO API errors"""

    pass


class USPTOAuthError(USPTOAPIError):
    """Authentication/API key error"""

    pass


class USPTOClient:
    """Client for USPTO Open Data Portal API

    The USPTO API provides access to patent application and grant data.
    Requires an API key from https://data.uspto.gov/myodp

    See https://data.uspto.gov/apis/getting-started for setup instructions.
    """

    BASE_URL = "https://api.uspto.gov/api/v1/patent"
    DEFAULT_TIMEOUT = 30

    def __init__(self, api_key: Optional[str] = None):
        """Initialize USPTO API client

        Args:
            api_key: USPTO API key. If not provided, will look for USPTO_API_KEY env var
        """
        self.api_key = api_key or os.getenv("USPTO_API_KEY")
        if not self.api_key:
            print(
                "WARNING: No USPTO API key provided. Set USPTO_API_KEY environment variable.",
                file=sys.stderr,
            )
            print("Get your API key at: https://data.uspto.gov/myodp", file=sys.stderr)

        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Set default headers
        if self.api_key:
            self.session.headers.update(
                {
                    "X-API-KEY": self.api_key,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to USPTO API with error handling

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            JSON response as dictionary

        Raises:
            USPTOAuthError: If authentication fails
            USPTOAPIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)

        try:
            response = self.session.request(method, url, **kwargs)

            # Handle authentication errors with detailed diagnostics
            if response.status_code == 401:
                raise USPTOAuthError(
                    "Authentication failed. Check your USPTO API key.\n"
                    "1. Visit: https://data.uspto.gov/myodp\n"
                    "2. Create account or sign in\n"
                    "3. Copy your API key from the portal\n"
                    "4. Set environment variable: USPTO_API_KEY=your_key\n"
                    f"   Current key configured: {'Yes' if self.api_key else 'No'}"
                )
            elif response.status_code == 403:
                raise USPTOAuthError(
                    "Access forbidden. Your API key may be invalid or expired.\n"
                    "1. Verify your API key at: https://data.uspto.gov/myodp\n"
                    "2. Generate a new API key if needed\n"
                    "3. Update USPTO_API_KEY environment variable"
                )
            elif response.status_code == 413:
                raise USPTOAPIError(
                    "Request too large. The query or filters are too complex.\n"
                    "Try reducing:\n"
                    "- Number of filters\n"
                    "- Query complexity\n"
                    "- Result limit"
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "unknown")
                raise USPTOAPIError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds.\n"
                    "USPTO API has rate limits:\n"
                    "- 100 requests per minute (typical)\n"
                    "- Reduce request frequency or wait before retrying"
                )
            elif response.status_code == 500:
                raise USPTOAPIError(
                    "USPTO API server error (500).\n"
                    "This is a temporary issue on USPTO's end.\n"
                    "Try:\n"
                    "1. Wait a few minutes and retry\n"
                    "2. Check USPTO API status at: https://data.uspto.gov/myodp\n"
                    "3. Simplify your query if problem persists"
                )
            elif response.status_code == 503:
                raise USPTOAPIError(
                    "USPTO API temporarily unavailable (503).\n"
                    "The service is down for maintenance or overloaded.\n"
                    "Try:\n"
                    "1. Wait and retry later\n"
                    "2. Check status at: https://data.uspto.gov/myodp"
                )

            # Raise for other HTTP errors with context
            response.raise_for_status()

            # Parse JSON response
            try:
                result = response.json()
            except ValueError as e:
                raise USPTOAPIError(
                    f"Invalid JSON response from USPTO API: {e}\n"
                    f"Status code: {response.status_code}\n"
                    f"Response text: {response.text[:200]}"
                )

            # Check for empty results and provide context
            if isinstance(result, dict) and result.get("results") is not None:
                if len(result["results"]) == 0:
                    # Empty results - provide diagnostic context
                    total_hits = result.get("totalHits", 0)
                    if total_hits == 0:
                        # Truly no matches - this is informational, not an error
                        pass
                    else:
                        # Has matches but results are empty (pagination issue?)
                        pass

            return result

        except requests.exceptions.Timeout:
            raise USPTOAPIError(
                f"Request timed out after {self.DEFAULT_TIMEOUT}s.\n"
                f"USPTO API did not respond in time.\n"
                f"Try:\n"
                f"1. Check your internet connection\n"
                f"2. Retry the request\n"
                f"3. Simplify the query if timeout persists"
            )
        except requests.exceptions.ConnectionError as e:
            raise USPTOAPIError(
                f"Connection failed to USPTO API: {e}\n"
                f"Try:\n"
                f"1. Check your internet connection\n"
                f"2. Verify firewall/proxy settings\n"
                f"3. Test connection: curl -I https://api.data.uspto.gov"
            )
        except USPTOAuthError:
            # Re-raise auth errors as-is
            raise
        except USPTOAPIError:
            # Re-raise API errors as-is
            raise
        except requests.exceptions.RequestException as e:
            # Catch-all for other request errors
            raise USPTOAPIError(f"Request failed: {e}\n" f"URL: {url}\n" f"Method: {method}")

    def search_patents(
        self,
        query: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        range_filters: Optional[List[Dict[str, Any]]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        fields: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 25,
        facets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Search patents using USPTO Open Data Portal API

        Args:
            query: Free-form search query or field-specific query using DSL
                   Examples:
                   - "artificial intelligence" (free-form)
                   - "applicationMetaData.applicationTypeLabelName:Utility" (field-specific)
            filters: List of exact match filters
                     Example: [{"name": "applicationMetaData.applicationTypeLabelName",
                               "value": ["Utility"]}]
            range_filters: List of range filters for dates/numbers
                          Example: [{"field": "applicationMetaData.grantDate",
                                    "valueFrom": "2020-01-01", "valueTo": "2025-01-01"}]
            sort: Sort order. Example: [{"field": "applicationMetaData.filingDate",
                                        "order": "desc"}]
            fields: List of fields to include in response
            offset: Starting position (default: 0)
            limit: Number of results (default: 25, max: 100)
            facets: List of fields to aggregate/facet

        Returns:
            Dictionary containing:
            - results: List of patent records
            - totalHits: Total number of matches
            - facets: Aggregation results (if requested)

        Raises:
            USPTOAPIError: If search fails
        """
        # Build POST request body
        body: Dict[str, Any] = {
            "pagination": {"offset": offset, "limit": min(limit, 100)}  # Cap at 100
        }

        if query:
            body["q"] = query
        if filters:
            body["filters"] = filters
        if range_filters:
            body["rangeFilters"] = range_filters
        if sort:
            body["sort"] = sort
        if fields:
            body["fields"] = fields
        if facets:
            body["facets"] = facets

        return self._make_request("POST", "applications/search", json=body)

    def search_patents_simple(
        self,
        query: str,
        limit: int = 25,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        application_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[PatentSearchResult]:
        """Simplified patent search with common filters

        Args:
            query: Search query (free-form or field-specific)
            limit: Number of results (default: 25)
            start_year: Filter patents from this year onwards
            end_year: Filter patents up to this year
            application_type: Filter by type (Utility, Design, Plant, Re-Issue)
            status: Filter by status (e.g., "Patented Case", "Abandoned")

        Returns:
            List of PatentSearchResult objects
        """
        filters = []
        range_filters = []

        # Add application type filter
        if application_type:
            filters.append(
                {
                    "name": "applicationMetaData.applicationTypeLabelName",
                    "value": [application_type],
                }
            )

        # Add status filter
        if status:
            filters.append(
                {
                    "name": "applicationMetaData.applicationStatusDescriptionText",
                    "value": [status],
                }
            )

        # Add year range filter
        if start_year or end_year:
            range_filter: Dict[str, Any] = {"field": "applicationMetaData.grantDate"}
            if start_year:
                range_filter["valueFrom"] = f"{start_year}-01-01"
            else:
                range_filter["valueFrom"] = "1976-01-01"  # Start of electronic records

            if end_year:
                range_filter["valueTo"] = f"{end_year}-12-31"
            else:
                range_filter["valueTo"] = f"{datetime.now().year}-12-31"

            range_filters.append(range_filter)

        # Perform search
        response = self.search_patents(
            query=query,
            filters=filters if filters else None,
            range_filters=range_filters if range_filters else None,
            limit=limit,
        )

        # Parse results
        results = []
        for item in response.get("results", []):
            results.append(self._parse_patent_result(item))

        return results

    def get_patent_by_number(self, patent_number: str) -> Optional[PatentSearchResult]:
        """Retrieve a specific patent by patent number

        Args:
            patent_number: USPTO patent number (e.g., "11234567")

        Returns:
            PatentSearchResult if found, None otherwise
        """
        # Search for exact patent number
        response = self.search_patents(
            filters=[{"name": "applicationMetaData.patentNumber", "value": [patent_number]}],
            limit=1,
        )

        results = response.get("results", [])
        if results:
            return self._parse_patent_result(results[0])
        return None

    def get_patent_by_application(self, application_number: str) -> Optional[PatentSearchResult]:
        """Retrieve a patent by application number

        Args:
            application_number: USPTO application number (e.g., "16/123,456")

        Returns:
            PatentSearchResult if found, None otherwise
        """
        # Clean application number (remove slashes)
        clean_app_num = application_number.replace("/", "").replace(",", "")

        response = self.search_patents(
            filters=[{"name": "applicationNumberText", "value": [clean_app_num]}],
            limit=1,
        )

        results = response.get("results", [])
        if results:
            return self._parse_patent_result(results[0])
        return None

    def _parse_patent_result(self, data: Dict[str, Any]) -> PatentSearchResult:
        """Parse patent data from API response into PatentSearchResult

        Args:
            data: Raw patent data from API

        Returns:
            PatentSearchResult object
        """
        app_meta = data.get("applicationMetaData", {})

        # Extract inventors
        inventors = []
        inventor_bag = app_meta.get("inventorBag", [])
        for inv in inventor_bag:
            name = inv.get("inventorNameText", "")
            if name:
                inventors.append(name)

        # Extract applicants
        applicants = []
        applicant_bag = app_meta.get("applicantBag", [])
        for app in applicant_bag:
            name = app.get("applicantNameText", "")
            if name:
                applicants.append(name)

        # Build result object
        return PatentSearchResult(
            application_number=data.get("applicationNumberText", ""),
            patent_number=app_meta.get("patentNumber"),
            filing_date=app_meta.get("filingDate"),
            grant_date=app_meta.get("grantDate"),
            title=app_meta.get("inventionTitle"),
            application_type=app_meta.get("applicationTypeLabelName"),
            status=app_meta.get("applicationStatusDescriptionText"),
            inventors=inventors,
            applicants=applicants,
            abstract=None,  # Not available in search results, requires separate API call
            raw_data=data,
        )

    def get_recent_patents(
        self, days: int = 7, application_type: str = "Utility", limit: int = 100
    ) -> List[PatentSearchResult]:
        """Get recently granted patents

        Args:
            days: Number of days to look back (default: 7)
            application_type: Type of patents (Utility, Design, Plant)
            limit: Maximum number of results

        Returns:
            List of recently granted patents
        """
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        response = self.search_patents(
            filters=[
                {
                    "name": "applicationMetaData.applicationTypeLabelName",
                    "value": [application_type],
                }
            ],
            range_filters=[
                {
                    "field": "applicationMetaData.grantDate",
                    "valueFrom": start_date.strftime("%Y-%m-%d"),
                    "valueTo": end_date.strftime("%Y-%m-%d"),
                }
            ],
            sort=[{"field": "applicationMetaData.grantDate", "order": "desc"}],
            limit=limit,
        )

        return [self._parse_patent_result(r) for r in response.get("results", [])]

    def check_api_status(self) -> bool:
        """Check if the API is accessible and the API key is valid

        Returns:
            True if API is working, False otherwise
        """
        try:
            # Make a simple search request
            self.search_patents(limit=1)
            return True
        except USPTOAuthError:
            print("ERROR: Invalid or missing USPTO API key", file=sys.stderr)
            return False
        except USPTOAPIError as e:
            print(f"ERROR: USPTO API error: {e}", file=sys.stderr)
            return False

    def check_api_status_detailed(self) -> Dict[str, Any]:
        """Check API status with detailed diagnostics

        Returns:
            Dictionary with status information:
            - available: bool (True if API is working)
            - api_key_configured: bool (True if API key is set)
            - error: Optional error message
            - message: Status message
            - response_time_ms: API response time in milliseconds
        """
        import time

        status = {
            "available": False,
            "api_key_configured": bool(self.api_key),
            "error": None,
            "message": "",
            "response_time_ms": None,
        }

        if not self.api_key:
            status["message"] = "USPTO API key not configured"
            status["error"] = (
                "Set USPTO_API_KEY environment variable.\n"
                "Get your key at: https://data.uspto.gov/myodp"
            )
            return status

        try:
            # Measure response time
            start_time = time.time()
            response = self.search_patents(limit=1)
            end_time = time.time()

            status["response_time_ms"] = int((end_time - start_time) * 1000)
            status["available"] = True
            status["message"] = f"USPTO API operational (response: {status['response_time_ms']}ms)"

            # Check if we got results
            total_hits = response.get("totalHits", 0)
            if total_hits == 0:
                status["message"] += " - Note: Test query returned 0 results (expected)"

        except USPTOAuthError as e:
            status["message"] = "Authentication failed"
            status["error"] = str(e)
        except USPTOAPIError as e:
            status["message"] = "API request failed"
            status["error"] = str(e)
        except Exception as e:
            status["message"] = "Unexpected error"
            status["error"] = f"Unexpected error checking USPTO API: {e}"

        return status


def format_patent_result(patent: PatentSearchResult, verbose: bool = False) -> str:
    """Format a patent search result for display

    Args:
        patent: PatentSearchResult object
        verbose: If True, include additional details

    Returns:
        Formatted string representation
    """
    lines = []

    # Title and numbers
    if patent.title:
        lines.append(f"Title: {patent.title}")

    if patent.patent_number:
        lines.append(f"Patent Number: {patent.patent_number}")

    lines.append(f"Application Number: {patent.application_number}")

    # Dates
    if patent.filing_date:
        lines.append(f"Filing Date: {patent.filing_date}")
    if patent.grant_date:
        lines.append(f"Grant Date: {patent.grant_date}")

    # Type and status
    if patent.application_type:
        lines.append(f"Type: {patent.application_type}")
    if patent.status:
        lines.append(f"Status: {patent.status}")

    # Inventors
    if patent.inventors:
        if len(patent.inventors) == 1:
            lines.append(f"Inventor: {patent.inventors[0]}")
        else:
            lines.append(f"Inventors: {', '.join(patent.inventors[:3])}")
            if len(patent.inventors) > 3:
                lines.append(f"  ... and {len(patent.inventors) - 3} more")

    # Applicants
    if patent.applicants and verbose:
        if len(patent.applicants) == 1:
            lines.append(f"Applicant: {patent.applicants[0]}")
        else:
            lines.append(f"Applicants: {', '.join(patent.applicants[:3])}")
            if len(patent.applicants) > 3:
                lines.append(f"  ... and {len(patent.applicants) - 3} more")

    return "\n".join(lines)


if __name__ == "__main__":
    """Test USPTO API client"""

    print("=" * 60)
    print("USPTO API CLIENT TEST")
    print("=" * 60)

    # Initialize client
    client = USPTOClient()

    # Check API status
    print("\nChecking API status...")
    if not client.check_api_status():
        print("\nTo use the USPTO API:")
        print("1. Create account at: https://data.uspto.gov/myodp")
        print("2. Verify with ID.me")
        print("3. Get your API key")
        print("4. Set environment variable: USPTO_API_KEY=your_key_here")
        sys.exit(1)

    print("✓ API key is valid")

    # Test simple search
    print("\n" + "=" * 60)
    print("TEST: Search for 'artificial intelligence' patents")
    print("=" * 60)

    try:
        results = client.search_patents_simple(
            query="artificial intelligence",
            limit=5,
            start_year=2024,
            application_type="Utility",
        )

        print(f"\nFound {len(results)} patents:")
        for i, patent in enumerate(results, 1):
            print(f"\n--- Patent {i} ---")
            print(format_patent_result(patent))

    except USPTOAPIError as e:
        print(f"Search failed: {e}")
