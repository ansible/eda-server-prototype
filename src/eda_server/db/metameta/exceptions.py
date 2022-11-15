

class MetaMetaException(Exception):
    pass

class MetaMetaNotFound(MetaMetaException):
    _item_type = "item"
    def __init__(self, *args):
        if len(args) < 1:
            raise MetaMetaException(
                "{0} exceptions requires a key argument".format(
                    self.__class__.__name__
                )
            )

        new_args = tuple(
            m for m in (
                "No {0} type named '{1}' was registered.".format(
                    self._item_type,
                    args[0]
                ),
                " ".join(args[1:])
            )
            if m
        )
        super().__init__(*new_args)

class MetaMetaEngineNotFound(MetaMetaNotFound):
    _item_type = "engine"

class MetaMetaSchemaNotFound(MetaMetaNotFound):
    _item_type = "schema"

class MetaMetaTableNotFound(MetaMetaNotFound):
    _item_type = "table"
