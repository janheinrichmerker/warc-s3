from io import BytesIO
from pathlib import Path
from random import Random
from typing import Iterator, List

from moto import mock_aws
from pytest import MonkeyPatch, fixture, raises, warns
from warcio import WARCWriter
from warcio.recordloader import ArcWarcRecord as WarcRecord

from warc_s3 import WarcS3Location, WarcS3Store, _write_records

_BUCKET_NAME = "test-bucket"
_CREDENTIAL = "test"


def _payload(index: int, payload_size: int = 100) -> bytes:
    # Random payload, so that compression does not shrink it much.
    return Random(index).getrandbits(  # noqa: S311
        8 * payload_size
    ).to_bytes(payload_size, "big")


def _create_records(count: int, payload_size: int = 100) -> List[WarcRecord]:
    writer = WARCWriter(BytesIO(), gzip=False)
    return [
        writer.create_warc_record(
            uri=f"https://example.com/{i}",
            record_type="resource",
            payload=BytesIO(_payload(i, payload_size)),
            warc_content_type="text/plain",
        )
        for i in range(count)
    ]


@fixture(autouse=True)
def no_s3cfg(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("warc_s3._S3CFG_PATH", tmp_path / ".s3cfg")


@fixture
def store() -> Iterator[WarcS3Store]:
    with mock_aws():
        with WarcS3Store(
            bucket_name=_BUCKET_NAME,
            access_key=_CREDENTIAL,
            secret_key=_CREDENTIAL,
            quiet=True,
        ) as store:
            yield store


def test_write_records_contiguous_locations() -> None:
    records = _create_records(5)
    file = BytesIO()
    written = list(
        _write_records(
            records=records,
            file=file,
            key="test.warc.gz",
            max_file_size=1_000_000,
            max_file_records=None,
        )
    )
    assert [
        written_record.record.rec_headers.get_header("WARC-Target-URI")
        for written_record in written
    ] == [f"https://example.com/{i}" for i in range(5)]
    assert [
        written_record.record.content_stream().read() for written_record in written
    ] == [_payload(i) for i in range(5)]
    locations = [written_record.location for written_record in written]
    assert all(location is not None for location in locations)
    for previous, current in zip(locations, locations[1:]):
        assert previous is not None and current is not None
        assert current.offset == previous.offset + previous.length
    last = locations[-1]
    assert last is not None
    assert last.offset + last.length == file.tell()


def test_write_records_max_file_records() -> None:
    records = _create_records(5)
    written = list(
        _write_records(
            records=records,
            file=BytesIO(),
            key="test.warc.gz",
            max_file_size=1_000_000,
            max_file_records=2,
        )
    )
    assert [
        written_record.record.rec_headers.get_header("WARC-Target-URI")
        for written_record in written
    ] == [f"https://example.com/{i}" for i in range(5)]
    assert [
        written_record.record.content_stream().read() for written_record in written
    ] == [_payload(i) for i in range(5)]
    assert [written_record.location is not None for written_record in written] == [
        True, True, False, False, False
    ]


def test_write_records_max_file_size() -> None:
    records = _create_records(5, payload_size=1_000)
    written = list(
        _write_records(
            records=records,
            file=BytesIO(),
            key="test.warc.gz",
            max_file_size=3_000,
            max_file_records=None,
        )
    )
    assert [
        written_record.record.rec_headers.get_header("WARC-Target-URI")
        for written_record in written
    ] == [record.rec_headers.get_header("WARC-Target-URI") for record in records]
    assert [written_record.location is not None for written_record in written] == [
        True, True, False, False, False
    ]
    assert [
        written_record.record.content_stream().read() for written_record in written
    ] == [_payload(i, 1_000) for i in range(5)]


def test_write_records_warns_low_max_file_size() -> None:
    records = _create_records(1)
    with warns(UserWarning, match="Very low max file size"):
        written = list(
            _write_records(
                records=records,
                file=BytesIO(),
                key="test.warc.gz",
                max_file_size=10,
                max_file_records=None,
            )
        )
    assert len(written) == 1
    assert written[0].location is None
    assert (
        written[0].record.rec_headers.get_header("WARC-Target-URI")
        == "https://example.com/0"
    )
    assert written[0].record.content_stream().read() == _payload(0)


def test_missing_credentials() -> None:
    with mock_aws():
        with raises(ValueError, match="access key"):
            WarcS3Store(bucket_name=_BUCKET_NAME, secret_key=_CREDENTIAL)
        with raises(ValueError, match="secret key"):
            WarcS3Store(bucket_name=_BUCKET_NAME, access_key=_CREDENTIAL)


def test_creates_bucket(store: WarcS3Store) -> None:
    store.client.head_bucket(Bucket=_BUCKET_NAME)


def test_write_and_read(store: WarcS3Store) -> None:
    written = list(store.write(_create_records(3)))
    assert len(written) == 3
    assert len({written_record.location.key for written_record in written}) == 1
    for i, written_record in enumerate(written):
        assert written_record.record.content_stream().read() == _payload(i)
        with store.read(written_record.location) as read_record:
            assert (
                read_record.rec_headers.get_header("WARC-Target-URI")
                == f"https://example.com/{i}"
            )
            assert read_record.content_stream().read() == _payload(i)


def test_write_splits_files(store: WarcS3Store) -> None:
    split_store = WarcS3Store(
        bucket_name=_BUCKET_NAME,
        access_key=_CREDENTIAL,
        secret_key=_CREDENTIAL,
        max_file_records=2,
        quiet=True,
    )
    written = list(split_store.write(_create_records(5)))
    assert len(written) == 5
    keys = [written_record.location.key for written_record in written]
    assert len(set(keys)) == 3
    listed = store.client.list_objects_v2(Bucket=_BUCKET_NAME)["Contents"]
    assert {obj["Key"] for obj in listed} == set(keys)


def test_write_splits_files_by_size(store: WarcS3Store) -> None:
    split_store = WarcS3Store(
        bucket_name=_BUCKET_NAME,
        access_key=_CREDENTIAL,
        secret_key=_CREDENTIAL,
        max_file_size=3_000,
        quiet=True,
    )
    written = list(split_store.write(_create_records(5, payload_size=1_000)))
    assert len(written) == 5
    assert len({written_record.location.key for written_record in written}) == 3
    for i, written_record in enumerate(written):
        with split_store.read(written_record.location) as read_record:
            assert read_record.content_stream().read() == _payload(i, 1_000)


def test_write_record_too_large(store: WarcS3Store) -> None:
    small_store = WarcS3Store(
        bucket_name=_BUCKET_NAME,
        access_key=_CREDENTIAL,
        secret_key=_CREDENTIAL,
        max_file_size=1_000,
        quiet=True,
    )
    with raises(ValueError, match="does not fit"):
        list(small_store.write(_create_records(1, payload_size=1_000)))
    listed = store.client.list_objects_v2(Bucket=_BUCKET_NAME)
    assert listed.get("KeyCount") == 0


def test_write_empty(store: WarcS3Store) -> None:
    assert list(store.write([])) == []
    listed = store.client.list_objects_v2(Bucket=_BUCKET_NAME)
    assert listed.get("KeyCount") == 0


def test_read_location_is_named_tuple() -> None:
    location = WarcS3Location(key="a.warc.gz", offset=1, length=2)
    assert tuple(location) == ("a.warc.gz", 1, 2)
