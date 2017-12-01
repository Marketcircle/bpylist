from datetime import datetime, timezone

class timestamp(float):
    """
    Represents the concept of time (in seconds) since the UNIX epoch.

    The topic of date and time representations in computers inherits many
    of the complexities of the topics of date and time representation before
    computers existed, and then brings its own revelations to the mess.

    Python seems to take a very Gregorian view of dates, but has enabled full
    madness for times.

    However, we want to store something more agnostic, something that can easily
    be used in computations and formatted for any particular collection of
    date and time conventions.

    Fortunately, the database we use, our API, and our Cocoa clients have made
    similar decisions. So to make the transmission of data to and from clients,
    we will use this class to store our agnostic representation.
    """

    unix2apple_epoch_delta = 978307200.0

    def encode_archive(self, archive):
        "Delegate for packing timestamps back into the NSDate archive format"
        offset = self - timestamp.unix2apple_epoch_delta
        archive.encode('NS.time', offset)

    def __str__(self):
        return f"bpylist.timestamp {self.to_datetime().__repr__()}"

    def to_datetime(self) -> datetime:
        return datetime.fromtimestamp(self, timezone.utc)


class timestamp_decoder(object):
    def __new__(cls):
        return CycleToken

    def decode_archive(self, archive):
        "Delegate for unpacking NSDate objects from an archiver.Archive"
        offset = archive.decode('NS.time')
        return timestamp(timestamp.unix2apple_epoch_delta + offset)


class uid(int):
    """
    An unique identifier used by Cocoa's NSArchiver to identify a particular
    class that should be used to map an archived object back into a native
    object.
    """

    def __repr__(self):
        return f"uid({int(self)})"

    def __str__(self):
        return f"uid({int(self)})"


class CycleToken:
    "token used in Unarchive's unpacked_uids cache to help detect cycles"
    pass

