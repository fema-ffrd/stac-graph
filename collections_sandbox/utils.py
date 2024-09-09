"""Utils for working with STAC items/catalogs copied here
(temporarily) from multiple existing fema-ffrd and dewberry repos. 
"""

import logging
import os
from typing import List
from urllib.parse import quote

import boto3
import boto3.session
import botocore
import pystac
import requests
from mypy_boto3_s3.service_resource import ObjectSummary

logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)


def str_from_s3(ras_text_file_path: str, client, bucket) -> str:
    """Read a text file from s3 and return its contents as a string."""
    logging.debug(f"reading: {ras_text_file_path}")
    response = client.get_object(Bucket=bucket, Key=ras_text_file_path)
    return response["Body"].read().decode("utf-8")


def list_keys(s3_client: boto3.Session.client, bucket: str, prefix: str, suffix: str = "") -> list:
    """List all keys in an S3 bucket with a given prefix and suffix."""
    keys = []
    kwargs = {"Bucket": bucket, "Prefix": prefix}
    while True:
        resp = s3_client.list_objects_v2(**kwargs)
        keys += [obj["Key"] for obj in resp["Contents"] if obj["Key"].endswith(suffix)]
        try:
            kwargs["ContinuationToken"] = resp["NextContinuationToken"]
        except KeyError:
            break
    return keys


def init_s3_resources() -> tuple:
    """Establish a boto3 (AWS) session and return the session, S3 client, and S3 resource handles."""
    # Instantitate S3 resources
    session = boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )

    s3_client = session.client("s3")
    s3_resource = session.resource("s3")
    return session, s3_client, s3_resource


def get_basic_object_metadata(obj: ObjectSummary) -> dict:
    """
    Retrieve basic metadata of an AWS S3 object.

    Parameters
    ----------
        obj (ObjectSummary): The AWS S3 object.

    Returns
    -------
        dict: A dictionary with the size, ETag, last modified date, storage platform, region, and storage tier of the object.
    """
    try:
        _ = obj.load()
        return {
            "file:size": obj.content_length,
            "e_tag": obj.e_tag.strip('"'),
            "last_modified": obj.last_modified.isoformat(),
            "storage:platform": "AWS",
            "storage:region": obj.meta.client.meta.region_name,
            "storage:tier": obj.storage_class,
        }
    except botocore.exceptions.ClientError:
        raise KeyError(f"Unable to access {obj.key} check that key exists and you have access")


def split_s3_key(s3_key: str) -> tuple[str, str]:
    """
    Split an S3 key into the bucket name and the key.

    Parameters
    ----------
        s3_key (str): The S3 key to split. It should be in the format 's3://bucket/key'.

    Returns
    -------
        tuple: A tuple containing the bucket name and the key. If the S3 key does not contain a key, the second element
          of the tuple will be None.

    The function performs the following steps:
        1. Removes the 's3://' prefix from the S3 key.
        2. Splits the remaining string on the first '/' character.
        3. Returns the first part as the bucket name and the second part as the key. If there is no '/', the key will
          be None.
    """
    parts = s3_key.replace("s3://", "").split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else None
    return bucket, key


def s3_key_public_url_converter(url: str, dev_mode: bool = False) -> str:
    """
    Convert an S3 URL to an HTTPS URL and vice versa.

    Args:
    ----------
        url (str): The URL to convert. It should be in the format 's3://bucket/' or 'https://bucket.s3.amazonaws.com/'.
        dev_mode (bool): A flag indicating whether the function should use the Minio endpoint for S3 URL conversion.
    Return:
    -------
        str: The converted URL. If the input URL is an S3 URL, the function returns an HTTPS URL. If the input URL is
        an HTTPS URL, the function returns an S3 URL.

    The function performs the following steps:
        1. Checks if the input URL is an S3 URL or an HTTPS URL.
        2. If the input URL is an S3 URL, it converts it to an HTTPS URL.
        3. If the input URL is an HTTPS URL, it converts it to an S3 URL.
    """
    if url.startswith("s3"):
        bucket = url.replace("s3://", "").split("/")[0]
        key = url.replace(f"s3://{bucket}", "")[1:]
        if dev_mode:
            logging.info(f"dev_mode | using minio endpoint for s3 url conversion: {url}")
            return f"{os.environ.get('MINIO_S3_ENDPOINT')}/{bucket}/{key}"
        else:
            return f"https://{bucket}.s3.amazonaws.com/{key}"

    elif url.startswith("http"):
        if dev_mode:
            logging.info(f"dev_mode | using minio endpoint for s3 url conversion: {url}")
            bucket = url.replace(os.environ.get("MINIO_S3_ENDPOINT"), "").split("/")[0]
            key = url.replace(os.environ.get("MINIO_S3_ENDPOINT"), "")
        else:
            bucket = url.replace("https://", "").split(".s3.amazonaws.com")[0]
            key = url.replace(f"https://{bucket}.s3.amazonaws.com/", "")

        return f"s3://{bucket}/{key}"

    else:
        raise ValueError(f"Invalid URL format: {url}")


def extract_bucketname_and_keyname(s3path: str) -> tuple[str, str]:
    """Parse the provided s3:// object path and return its bucket name and key."""
    if not s3path.startswith("s3://"):
        raise ValueError(f"s3path does not start with s3://: {s3path}")
    bucket, _, key = s3path[5:].partition("/")
    return bucket, key


def key_to_uri(key: str, bucket: str) -> str:
    """Convert a key to a uri."""
    return f"https://{bucket}.s3.amazonaws.com/{quote(key)}"


def uri_to_key(href: str, bucket: str) -> str:
    """Convert a uri to a key."""
    return href.replace(f"https://{bucket}.s3.amazonaws.com/", "")


def collection_exists(endpoint: str, collection_id: str):
    """Check if a collection exists in a STAC API."""
    return requests.get(f"{endpoint}/collections/{collection_id}")


def create_collection(
    models: List[pystac.Item], id: str, description: str = None, title: str = None
) -> pystac.Collection:
    """Create a STAC collection from a list of STAC items."""
    extent = pystac.Extent.from_items(models)
    return pystac.Collection(
        id=id,
        description=description,
        title=title,
        extent=extent,
    )


def upsert_collection(endpoint: str, collection: pystac.Collection, headers: dict):
    """Upsert a collection to a STAC API."""
    collections_url = f"{endpoint}/collections"
    response = requests.post(collections_url, json=collection.to_dict(), headers=headers)
    if response.status_code == 409:
        logging.warning("collection already exists, updating...")
        collections_update_url = f"{collections_url}/{collection.id}"
        response = requests.put(collections_update_url, json=collection.to_dict(), headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Error putting collection {(response.status_code)}")
    elif response.status_code not in (201, 200):
        raise RuntimeError(f"Error posting collection {(response.status_code)}")


def upsert_item(endpoint: str, collection_id: str, item: pystac.Item, headers: dict):
    """Upsert an item to a STAC API."""
    items_url = f"{endpoint}/collections/{collection_id}/items"
    response = requests.post(items_url, json=item.to_dict(), headers=headers)

    if response.status_code == 409:
        item_update_url = f"{items_url}/{item.id}"
        response = requests.put(item_update_url, json=item.to_dict(), headers=headers)
    elif response.status_code != 200:
        return f"Response from STAC API: {response.status_code}"
    if not response.ok:
        return f"Response from STAC API: {response.status_code}"


def delete_collection(endpoint: str, collection_id: str, headers: dict):
    """Upsert a collection to a STAC API."""
    collections_url = f"{endpoint}/collections/{collection_id}"
    return requests.delete(collections_url, headers=headers)
