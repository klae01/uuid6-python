r"""UUID draft version objects (universally unique identifiers).
This module provides the functions uuid6() and uuid7() for
generating version 6 and 7 UUIDs as specified in
https://github.com/uuid6/uuid6-ietf-draft.
"""

import math
import secrets
import time
from uuid import UUID


class DraftUUID(UUID):
    r"""UUID draft version objects"""

    def __init__(self, int: int, version: int = None) -> None:
        r"""Create a UUID from a single 128-bit integer as the 'int' argument."""

        if not 0 <= int < 1 << 128:
            raise ValueError("int is out of range (need a 128-bit value)")
        if version is not None:
            if not 6 <= version <= 7:
                raise ValueError("illegal version number")
            # Set the variant to RFC 4122.
            int &= ~(0xC000 << 48)
            int |= 0x8000 << 48
            # Set the version number.
            int &= ~(0xF000 << 64)
            int |= version << 76
        super().__init__(int=int)

    @property
    def subsec(self) -> int:
        return (
            (self.time_mid & 0x0FFF) << 18
            | (self.time_hi_version & 0x0FFF) << 6
            | self.clock_seq_hi_variant & 0x3F
        )

    @property
    def time(self) -> int:
        if self.version == 6:
            return (
                (self.time_low << 28)
                | (self.time_mid << 12)
                | (self.time_hi_version & 0x0FFF)
            )
        if self.version == 7:
            return self.unixts * 10 ** 9 + _subsec_decode(self.subsec)
        return super().time

    @property
    def unixts(self) -> int:
        return self.time_low << 4 | self.time_mid >> 12


def _getrandbits(k: int) -> int:
    return secrets.randbits(k)


def _subsec_decode(value: int) -> int:
    return math.ceil(value * 10 ** 9 / 2 ** 30)


def _subsec_encode(value: int) -> int:
    return value * 2 ** 30 // 10 ** 9


_last_v6_timestamp = None
_last_v7_timestamp = None


def uuid6(clock_seq: int = None) -> UUID:
    r"""Generate a UUID from sequence number, and the current time.
    If 'clock_seq' is given, it is used as the sequence number;
    otherwise a random 14-bit sequence number is chosen."""

    global _last_v6_timestamp

    nanoseconds = time.time_ns()
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds // 100 + 0x01B21DD213814000
    if _last_v6_timestamp is not None and timestamp <= _last_v6_timestamp:
        timestamp = _last_v6_timestamp + 1
    _last_v6_timestamp = timestamp
    if clock_seq is None:
        clock_seq = _getrandbits(14)  # instead of stable storage
    node = _getrandbits(48)
    time_high_and_time_mid = (timestamp >> 12) & 0xFFFFFFFFFFFF
    time_low_and_version = timestamp & 0x0FFF
    uuid_int = time_high_and_time_mid << 80
    uuid_int |= time_low_and_version << 64
    uuid_int |= (clock_seq & 0x3FFF) << 48
    uuid_int |= node
    return DraftUUID(int=uuid_int, version=6)


def uuid7() -> UUID:
    r"""The UUIDv7 format is designed to encode a Unix timestamp with
    arbitrary sub-second precision.  The key property provided by UUIDv7
    is that timestamp values generated by one system and parsed by
    another are guaranteed to have sub-second precision of either the
    generator or the parser, whichever is less.  Additionally, the system
    parsing the UUIDv7 value does not need to know which precision was
    used during encoding in order to function correctly."""

    global _last_v7_timestamp

    nanoseconds = time.time_ns()
    if _last_v7_timestamp is not None and nanoseconds <= _last_v7_timestamp:
        nanoseconds = _last_v7_timestamp + 1
    _last_v7_timestamp = nanoseconds
    timestamp_s, timestamp_ns = divmod(nanoseconds, 10 ** 9)
    subsec = _subsec_encode(timestamp_ns)
    subsec_a = subsec >> 18
    subsec_b = (subsec >> 6) & 0x0FFF
    subsec_c = subsec & 0x3F
    rand = _getrandbits(56)
    uuid_int = (timestamp_s & 0x0FFFFFFFFF) << 92
    uuid_int |= subsec_a << 80
    uuid_int |= subsec_b << 64
    uuid_int |= subsec_c << 56
    uuid_int |= rand
    return DraftUUID(int=uuid_int, version=7)
