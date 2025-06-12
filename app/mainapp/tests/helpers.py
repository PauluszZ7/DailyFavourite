import datetime
import random
import uuid
from dataclasses import fields, is_dataclass
from typing import get_args, get_origin

TEST_DATE = datetime.datetime.now().replace(microsecond=0)


def create_dummy_instance(cls):
    def gen_dummy(field):
        typ = field.type

        if get_origin(typ) is list:
            inner = get_args(typ)[0]
            return [create_dummy_instance(inner)]

        if typ is str:
            return str(uuid.uuid4()) if field.name == "id" else "test"

        if typ is int:
            return random.randint(10000, 99999) if field.name == "id" else 1

        if typ is bool:
            return True

        if typ is datetime.datetime:
            return TEST_DATE

        if is_dataclass(typ):
            inst = create_dummy_instance(typ)
            if hasattr(inst, "id") and getattr(inst, "id", None) in [None, ""]:
                setattr(
                    inst,
                    "id",
                    (
                        str(uuid.uuid4())
                        if isinstance(getattr(inst, "id", ""), str)
                        else random.randint(10000, 99999)
                    ),
                )
            return inst

        return None

    return cls(**{f.name: gen_dummy(f) for f in fields(cls)})
