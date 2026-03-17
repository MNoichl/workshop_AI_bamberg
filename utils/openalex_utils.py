import ast
import json
import math
import re
import time
from datetime import datetime
from typing import Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote_plus, urlencode, urlparse
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

OPENALEX_API_BASE = "https://api.openalex.org"
DEFAULT_PER_PAGE = 100
DEFAULT_SELECT_FIELDS = (
    "id,doi,display_name,publication_year,publication_date,"
    "abstract_inverted_index,primary_location,primary_topic,type"
)
WINDOW_PARAMS = {"page", "cursor", "per_page", "per-page"}


def _split_filter_string(filter_string: str) -> list[str]:
    if not filter_string:
        return []

    parts: list[str] = []
    current: list[str] = []
    quote_char: Optional[str] = None

    for char in filter_string:
        if char in {"'", '"'}:
            if quote_char == char:
                quote_char = None
            elif quote_char is None:
                quote_char = char
            current.append(char)
            continue

        if char == "," and quote_char is None:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _canonicalize_filter_key(key: str) -> str:
    key = key.strip()
    if key.startswith("host_venue."):
        return key.replace("host_venue.", "primary_location.source.", 1)
    return key


def _canonicalize_sort_value(sort_value: str) -> str:
    items = []
    for item in _split_filter_string(sort_value):
        direction = ""
        field = item
        if item.startswith("-"):
            direction = "-"
            field = item[1:]
        elif ":" in item:
            field_name, field_direction = item.split(":", 1)
            field = field_name
            direction = f":{field_direction}"

        field = _canonicalize_filter_key(field)
        items.append(f"{direction}{field}" if direction.startswith("-") else f"{field}{direction}")

    return ",".join(items)


def _normalise_openalex_url(url: str) -> tuple[str, dict[str, str]]:
    parsed_url = urlparse(url.strip())
    if not parsed_url.scheme:
        raise ValueError("OpenAlex URL must include a scheme, for example https://openalex.org/works?...")

    path = parsed_url.path or "/works"
    if path.rstrip("/").endswith("/works") or path == "/works":
        api_url = f"{OPENALEX_API_BASE}/works"
    else:
        api_url = f"{OPENALEX_API_BASE}{path}"

    query_params = parse_qs(parsed_url.query, keep_blank_values=False)
    params: dict[str, str] = {}

    if "filter" in query_params:
        normalised_filters = []
        promoted_search: Optional[str] = None
        for part in _split_filter_string(query_params["filter"][0]):
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            key = _canonicalize_filter_key(key)
            if key == "default.search" and promoted_search is None:
                promoted_search = value
                continue
            normalised_filters.append(f"{key}:{value}")

        if normalised_filters:
            params["filter"] = ",".join(normalised_filters)
        if promoted_search and "search" not in query_params:
            params["search"] = promoted_search

    for key in ("search", "search.exact", "search.semantic", "sample", "seed", "group_by", "select", "sort"):
        if key in query_params:
            value = query_params[key][0]
            params[key] = _canonicalize_sort_value(value) if key == "sort" else value

    for key in ("page", "cursor", "api_key", "mailto", "include_xpac"):
        if key in query_params:
            params[key] = query_params[key][0]

    if "per_page" in query_params:
        params["per_page"] = query_params["per_page"][0]
    elif "per-page" in query_params:
        params["per_page"] = query_params["per-page"][0]

    return api_url, params


def openalex_url_to_pyalex_query(url: str):
    """
    Convert an OpenAlex web or API URL to a normalised OpenAlex API request.

    The function name is kept for backwards compatibility with older notebooks.

    Returns
    -------
    tuple[str, dict[str, str]]
        The API endpoint and normalised query parameters.
    """
    return _normalise_openalex_url(url)


def _request_openalex_json(
    api_url: str,
    params: dict[str, str],
    *,
    context: str,
    timeout: int = 60,
    max_retries: int = 5,
) -> dict:
    cleaned_params = {key: value for key, value in params.items() if value not in (None, "")}
    full_url = api_url if not cleaned_params else f"{api_url}?{urlencode(cleaned_params)}"

    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        request = Request(
            full_url,
            headers={
                "Accept": "application/json",
                "User-Agent": "workshop_AI_bamberg/openalex-utils",
            },
        )

        try:
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            last_error = exc

            if exc.code in {429, 500, 502, 503, 504} and attempt < max_retries - 1:
                retry_after = exc.headers.get("Retry-After")
                wait_seconds = float(retry_after) if retry_after else 1.5 ** attempt
                time.sleep(wait_seconds)
                continue

            if exc.code in {401, 403}:
                raise RuntimeError(
                    "OpenAlex rejected the request. Add `api_key=...` to the function call "
                    f"for {context}. Response: {body or exc.reason}"
                ) from exc

            raise RuntimeError(
                f"OpenAlex request failed for {context} with status {exc.code}: {body or exc.reason}"
            ) from exc
        except URLError as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(1.5 ** attempt)
                continue
            raise RuntimeError(f"OpenAlex request failed for {context}: {exc}") from exc

    raise RuntimeError(f"OpenAlex request failed for {context}: {last_error}")


def _strip_window_params(params: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in params.items() if key not in WINDOW_PARAMS}


def _bool_to_string(value: Optional[bool]) -> Optional[str]:
    if value is None:
        return None
    return "true" if value else "false"


def _normalise_identifier(identifier: str) -> str:
    identifier = identifier.strip()
    if identifier.startswith("https://openalex.org/"):
        return identifier.rsplit("/", 1)[-1]
    return identifier


def _fetch_entity(entity_type: str, identifier: str, *, api_key: Optional[str] = None) -> Optional[dict]:
    entity_id = _normalise_identifier(identifier)
    api_url = f"{OPENALEX_API_BASE}/{entity_type}/{entity_id}"
    params = {"api_key": api_key} if api_key else {}
    try:
        return _request_openalex_json(api_url, params, context=f"{entity_type}/{entity_id}")
    except RuntimeError:
        return None


def invert_abstract(inv_index):
    """Reconstruct an abstract from OpenAlex' inverted index."""
    if isinstance(inv_index, str):
        try:
            inv_index = json.loads(inv_index)
        except Exception:
            try:
                inv_index = ast.literal_eval(inv_index)
            except Exception:
                inv_index = None

    if isinstance(inv_index, dict):
        indexed_tokens = [(token, position) for token, positions in inv_index.items() for position in positions]
        return " ".join(token for token, _ in sorted(indexed_tokens, key=lambda item: item[1]))

    return " "


def get_pub(primary_location):
    """Extract a publication/source name from a work record."""
    try:
        source = primary_location["source"]["display_name"]
        if source not in {"parsed_publication", "Deleted Journal"}:
            return source
    except Exception:
        pass
    return " "


def get_field(record):
    """Extract the primary subfield name from a work record."""
    try:
        field = record["primary_topic"]["subfield"]["display_name"]
        return field if field is not None else np.nan
    except Exception:
        return np.nan


def process_records_to_df(records):
    """
    Convert OpenAlex work records to a DataFrame with reconstructed abstracts.
    """
    records_df = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)

    if records_df.empty:
        return pd.DataFrame(
            columns=[
                "id",
                "doi",
                "title",
                "publication_year",
                "publication_date",
                "abstract",
                "parsed_publication",
                "field",
                "type",
            ]
        )

    if "title" not in records_df.columns and "display_name" in records_df.columns:
        records_df["title"] = records_df["display_name"]
    elif "title" not in records_df.columns:
        records_df["title"] = " "

    if "abstract" not in records_df.columns:
        if "abstract_inverted_index" in records_df.columns:
            records_df["abstract"] = [invert_abstract(value) for value in records_df["abstract_inverted_index"]]
        else:
            records_df["abstract"] = " "

    if "parsed_publication" not in records_df.columns:
        if "primary_location" in records_df.columns:
            records_df["parsed_publication"] = [get_pub(value) for value in records_df["primary_location"]]
        else:
            records_df["parsed_publication"] = " "

    if "field" not in records_df.columns and "primary_topic" in records_df.columns:
        records_df["field"] = [get_field(record) for record in records_df.to_dict("records")]

    records_df["abstract"] = records_df["abstract"].fillna(" ")
    records_df["title"] = records_df["title"].fillna(" ")
    records_df["parsed_publication"] = records_df["parsed_publication"].fillna(" ")

    if "id" in records_df.columns:
        records_df = records_df.drop_duplicates(subset=["id"]).reset_index(drop=True)
    else:
        records_df = records_df.drop_duplicates().reset_index(drop=True)

    return records_df


def openalex_url_to_filename(url: str) -> str:
    """
    Convert an OpenAlex URL to a readable filename stem with a timestamp.
    """
    _, params = _normalise_openalex_url(url)
    parts = []

    if "search" in params:
        clean_search = re.sub(r"[^\w\s-]", "", unquote_plus(params["search"]))
        parts.append(f"search_{'_'.join(clean_search.split())}")

    if "filter" in params:
        for filter_part in _split_filter_string(params["filter"]):
            if ":" not in filter_part:
                continue
            key, value = filter_part.split(":", 1)
            safe_key = key.replace(".", "_")
            safe_value = re.sub(r"[^\w\s-]", "", unquote_plus(value))
            safe_value = "_".join(safe_value.split())
            parts.append(f"{safe_key}_{safe_value}")

    if "sort" in params:
        parts.append(f"sort_{params['sort'].replace('.', '_').replace(',', '__')}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "__".join(part for part in parts if part) or "openalex_query"
    filename = f"{filename}__{timestamp}"
    return filename[:251] if len(filename) > 255 else filename


def _work_params(
    url: str,
    *,
    api_key: Optional[str] = None,
    email: Optional[str] = None,
    select: Optional[str] = DEFAULT_SELECT_FIELDS,
    include_xpac: Optional[bool] = None,
) -> tuple[str, dict[str, str]]:
    api_url, params = _normalise_openalex_url(url)
    if not api_url.endswith("/works"):
        raise ValueError("This helper currently expects an OpenAlex works URL.")

    if api_key:
        params["api_key"] = api_key
    if email:
        params["mailto"] = email
    if select and "select" not in params:
        params["select"] = select
    include_xpac_value = _bool_to_string(include_xpac)
    if include_xpac_value is not None:
        params["include_xpac"] = include_xpac_value

    return api_url, params


def _get_query_count(api_url: str, params: dict[str, str]) -> int:
    count_params = _strip_window_params(params)
    count_params.pop("sample", None)
    count_params.pop("seed", None)
    count_params["per_page"] = "1"
    data = _request_openalex_json(api_url, count_params, context="count query")
    return int(data.get("meta", {}).get("count", 0))


def _download_cursor_records(
    api_url: str,
    params: dict[str, str],
    *,
    limit: Optional[int] = None,
    description: str = "Downloading OpenAlex records",
    progress_cb: Optional[Callable[[float, str], None]] = None,
    progress_start: float = 0.0,
    progress_span: float = 1.0,
) -> list[dict]:
    records: list[dict] = []
    request_params = _strip_window_params(params)
    request_params["per_page"] = str(DEFAULT_PER_PAGE)
    request_params["cursor"] = "*"

    pbar = tqdm(total=limit, desc=description, unit="records") if limit else tqdm(desc=description, unit="records")

    while True:
        data = _request_openalex_json(api_url, request_params, context=description)
        page_results = data.get("results", [])

        if not page_results:
            break

        for record in page_results:
            records.append(record)
            pbar.update(1)

            if progress_cb and limit:
                fraction = len(records) / max(limit, 1)
                progress_cb(progress_start + progress_span * min(fraction, 1.0), description)

            if limit and len(records) >= limit:
                pbar.close()
                return records

        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        request_params["cursor"] = next_cursor

    pbar.close()
    return records


def _download_sample_records(
    api_url: str,
    params: dict[str, str],
    *,
    target_size: int,
    seed_value: str,
    description: str,
    progress_cb: Optional[Callable[[float, str], None]] = None,
    progress_start: float = 0.0,
    progress_span: float = 1.0,
) -> list[dict]:
    if target_size <= 0:
        return []

    try:
        base_seed = int(str(seed_value).strip()) if str(seed_value).strip() else 42
    except ValueError:
        base_seed = 42

    seen_ids: set[str] = set()
    sampled_records: list[dict] = []
    batch_number = 0

    while len(sampled_records) < target_size and batch_number < 20:
        batch_number += 1
        remaining = target_size - len(sampled_records)
        batch_size = min(remaining, 10000)

        batch_params = _strip_window_params(params)
        batch_params.update(
            {
                "per_page": str(DEFAULT_PER_PAGE),
                "sample": str(batch_size),
                "seed": str(base_seed + batch_number - 1),
            }
        )

        total_pages = math.ceil(batch_size / DEFAULT_PER_PAGE)
        pbar = tqdm(total=batch_size, desc=f"{description} batch {batch_number}", unit="records")

        for page in range(1, total_pages + 1):
            batch_params["page"] = str(page)
            data = _request_openalex_json(api_url, batch_params, context=f"{description} batch {batch_number}")

            for record in data.get("results", []):
                record_id = record.get("id")
                if record_id and record_id in seen_ids:
                    continue

                if record_id:
                    seen_ids.add(record_id)
                sampled_records.append(record)
                pbar.update(1)

                if progress_cb:
                    fraction = len(sampled_records) / max(target_size, 1)
                    progress_cb(progress_start + progress_span * min(fraction, 1.0), description)

                if len(sampled_records) >= target_size:
                    break

            if len(sampled_records) >= target_size:
                break

        pbar.close()

        if batch_size < 10000:
            break

    return sampled_records[:target_size]


def get_records_from_dois(
    doi_list,
    block_size: int = 100,
    *,
    api_key: Optional[str] = None,
    email: Optional[str] = None,
    select: Optional[str] = DEFAULT_SELECT_FIELDS,
    include_xpac: Optional[bool] = None,
) -> pd.DataFrame:
    """
    Download OpenAlex work records for a list of DOIs in blocks.
    """
    api_url = f"{OPENALEX_API_BASE}/works"
    records: list[dict] = []
    block_size = max(1, min(int(block_size), 100))

    cleaned_dois = []
    for doi in doi_list:
        if doi is None:
            continue
        doi_str = str(doi).strip()
        if not doi_str:
            continue
        doi_str = doi_str.replace("https://doi.org/", "").replace("http://doi.org/", "")
        cleaned_dois.append(doi_str)

    for index in tqdm(range(0, len(cleaned_dois), block_size), desc="Downloading DOI blocks", unit="block"):
        sublist = cleaned_dois[index : index + block_size]
        params = {
            "filter": f"doi:{'|'.join(sublist)}",
            "per_page": str(min(DEFAULT_PER_PAGE, len(sublist))),
        }
        if select:
            params["select"] = select
        if api_key:
            params["api_key"] = api_key
        if email:
            params["mailto"] = email
        include_xpac_value = _bool_to_string(include_xpac)
        if include_xpac_value is not None:
            params["include_xpac"] = include_xpac_value

        data = _request_openalex_json(api_url, params, context="DOI lookup")
        records.extend(data.get("results", []))

    return process_records_to_df(records)


def openalex_url_to_readable_name(url: str, *, api_key: Optional[str] = None) -> str:
    """
    Convert an OpenAlex URL to a short, human-readable description.
    """
    _, params = _normalise_openalex_url(url)
    parts = []
    year_range = None

    if "search" in params:
        search_term = unquote_plus(params["search"]).strip("\"'")
        parts.append(f"Search: '{search_term}'")

    if "filter" in params:
        for filter_part in _split_filter_string(params["filter"]):
            if ":" not in filter_part:
                continue

            key, value = filter_part.split(":", 1)
            decoded_value = unquote_plus(value).strip("\"'")

            if key == "title_and_abstract.search":
                parts.append(f"T&A: '{decoded_value}'")
            elif key == "publication_year":
                year_range = decoded_value
            elif key == "cites":
                cited_work = _fetch_entity("works", decoded_value, api_key=api_key)
                if cited_work:
                    authorships = cited_work.get("authorships") or []
                    author_name = "Unknown"
                    if authorships:
                        author_name = authorships[0].get("author", {}).get("display_name", "Unknown").split()[-1]
                    year = cited_work.get("publication_year", "Unknown")
                    parts.append(f"Cites: {author_name} ({year})")
                else:
                    parts.append(f"Cites: {decoded_value}")
            elif key in {"authorships.institutions.lineage", "authorships.institutions.id"}:
                institution = _fetch_entity("institutions", decoded_value, api_key=api_key)
                parts.append(
                    f"From: {institution.get('display_name', decoded_value)}" if institution else f"From: {decoded_value}"
                )
            elif key in {"authorships.author.id", "author.id"}:
                author = _fetch_entity("authors", decoded_value, api_key=api_key)
                parts.append(f"By: {author.get('display_name', decoded_value)}" if author else f"By: {decoded_value}")
            elif key == "type":
                parts.append(f"Type: {decoded_value.replace('-', ' ').title()}")
            elif key == "primary_location.source.id":
                source = _fetch_entity("sources", decoded_value, api_key=api_key)
                parts.append(f"In: {source.get('display_name', decoded_value)}" if source else f"In: {decoded_value}")
            else:
                clean_key = key.replace("_", " ").replace(".", " ").title()
                parts.append(f"{clean_key}: {decoded_value.replace('_', ' ')}")

    description = ", ".join(parts) if parts else "OpenAlex Query"
    if year_range:
        description = f"{description}, {year_range}" if parts else f"Works from {year_range}"

    return description if len(description) <= 60 else f"{description[:57]}..."


def download_openalex_records(
    text_input: str,
    reduce_sample: bool = False,
    sample_reduction_method: str = "All",
    sample_size: int = 0,
    seed_value: str = "42",
    progress: Optional[Callable[[float, str], None]] = None,
    *,
    api_key: Optional[str] = None,
    email: Optional[str] = None,
    select: Optional[str] = DEFAULT_SELECT_FIELDS,
    include_xpac: Optional[bool] = None,
) -> pd.DataFrame:
    """
    Download OpenAlex work records for one or more OpenAlex URLs separated by ';'.
    """
    if not text_input or text_input.isspace():
        raise ValueError(
            "Error: Please enter a valid OpenAlex works URL in the OpenAlex-search field."
        )

    urls = [url.strip() for url in text_input.split(";") if url.strip()]
    if not urls:
        raise ValueError("No valid OpenAlex URLs were provided.")

    method = sample_reduction_method.strip() if sample_reduction_method else "All"
    if method not in {"All", "First n samples", "n random samples"}:
        raise ValueError("sample_reduction_method must be 'All', 'First n samples', or 'n random samples'.")

    def _noop_progress(_: float, __: str = "") -> None:
        return None

    progress_cb = progress or _noop_progress
    progress_cb(0.05, "Starting OpenAlex download")

    records: list[dict] = []
    seen_ids: set[str] = set()
    first_filename = openalex_url_to_filename(urls[0])
    print(f"Filename: {first_filename}")

    for index, url in enumerate(urls, start=1):
        api_url, params = _work_params(
            url,
            api_key=api_key,
            email=email,
            select=select,
            include_xpac=include_xpac,
        )
        query_count = _get_query_count(api_url, params)
        query_label = f"Query {index}/{len(urls)}"
        print(f"{query_label}: {query_count} matching records")

        if reduce_sample and method == "First n samples":
            target_size = min(sample_size, query_count) if sample_size > 0 else query_count
        elif reduce_sample and method == "n random samples":
            target_size = min(sample_size, query_count) if sample_size > 0 else query_count
        else:
            target_size = query_count

        if method == "n random samples" and reduce_sample:
            query_records = _download_sample_records(
                api_url,
                params,
                target_size=target_size,
                seed_value=seed_value,
                description=f"Sampling {query_label}",
                progress_cb=progress_cb,
                progress_start=0.1 + ((index - 1) / max(len(urls), 1)) * 0.8,
                progress_span=0.8 / max(len(urls), 1),
            )
        else:
            limit = target_size if reduce_sample and method == "First n samples" else None
            query_records = _download_cursor_records(
                api_url,
                params,
                limit=limit,
                description=f"Downloading {query_label}",
                progress_cb=progress_cb,
                progress_start=0.1 + ((index - 1) / max(len(urls), 1)) * 0.8,
                progress_span=0.8 / max(len(urls), 1),
            )

        for record in query_records:
            record_id = record.get("id")
            if record_id and record_id in seen_ids:
                continue
            if record_id:
                seen_ids.add(record_id)
            records.append(record)

    progress_cb(0.95, "Processing OpenAlex records")
    records_df = process_records_to_df(records)
    progress_cb(1.0, "Finished")
    print(f"Downloaded {len(records_df)} unique OpenAlex works")
    return records_df
