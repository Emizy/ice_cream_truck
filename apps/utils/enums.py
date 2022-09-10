class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [
            (c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__())
            for v in attrs
        ]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def get(c, value):
        if type(value) is int:
            try:
                return [
                    CustomEnum.Enum(k, v, c)
                    for k, v in c.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            except Exception:
                return None
        else:
            try:
                key = value.upper()
                return CustomEnum.Enum(key, c.__dict__[key], c)
            except Exception:
                return None

    @classmethod
    def key(c, key):
        try:
            return [value for name, value in c.__dict__.items() if name == key.upper()][
                0
            ]
        except Exception:
            return None

    @classmethod
    def items(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(v, c.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])


class UserTypeEnum(CustomEnum):
    COMPANY_OWNER = 'company'
    CUSTOMER = 'customer'
    FRANCHISE = 'franchise'

    @classmethod
    def choices(c):
        return (
            (c.CUSTOMER, 'Customer'),
            (c.COMPANY_OWNER, 'Company Owner'),
            (c.FRANCHISE, 'Franchise'),
        )


class StatusEnum(CustomEnum):
    DONE = 'done'
    NOT_DONE = 'not_done'

    @classmethod
    def choices(c):
        return (
            (c.DONE, "Done"),
            (c.NOT_DONE, "Not Done"),
        )
