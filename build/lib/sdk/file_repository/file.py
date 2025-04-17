import json


class File(object):

    def __init__(self, id, path, file_name, file_type, file_group, size, user, checksum, redacted, metadata,
                 created_date, modified_date):
        self.file_id = id
        self.path = path
        self.file_name = file_name
        self.file_type = file_type
        self.file_group = file_group
        self.size = size
        self.user = user
        self.checksum = checksum
        self.redacted = redacted
        self.metadata = metadata
        self.created_date = created_date
        self.modified_date = modified_date

    @classmethod
    def from_json(cls, obj):
        return cls(**obj)

    def to_json(self):
        return {
            "id": str(self.file_id),
            "file_name": self.file_name,
            "file_type": self.file_type,
            "path": self.path,
            "size": self.size,
            "file_group": self.file_group,
            "metadata": self.metadata,
            "user": self.user,
            "checksum": self.checksum,
            "redacted": self.redacted,
            "created_date": self.created_date,
            "modified_date": self.modified_date
        }

    def __str__(self):
        return f"{self.file_id}: {self.path} {self.file_group}"




