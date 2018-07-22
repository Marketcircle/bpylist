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

    @staticmethod
    def encode_archive(obj, archive):
        "Delegate for packing timestamps back into the NSDate archive format"
        offset = obj - timestamp.unix2apple_epoch_delta
        archive.encode('NS.time', offset)

    @staticmethod
    def decode_archive(archive):
        "Delegate for unpacking NSDate objects from an archiver.Archive"
        offset = archive.decode('NS.time')
        return timestamp(timestamp.unix2apple_epoch_delta + offset)

    def __str__(self):
        return f"bpylist.timestamp {self.to_datetime().__repr__()}"

    def to_datetime(self) -> datetime:
        return datetime.fromtimestamp(self, timezone.utc)


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


class NSMutableData:
    data: bytes

    def __init__(self, data: bytes) -> None:
        self.data = data

    def encode_archive(self, archive):
        archive.encode('NS.data', self.data)

    @staticmethod
    def decode_archive(archive):
        return NSMutableData(bytes(archive.decode('NS.data')))

    def __eq__(self, other):
        return self.data == other.data

    def __repr__(self):
        return "NSMutableData(%s bytes)" % (
            'null' if self.data is None else len(self.data))
