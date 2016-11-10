import yaml


YAML_DUMP_KWARGS = dict(explicit_start=False, default_flow_style=False)


class FieldsRegistry(object):

    def __init__(self):
        self._fields = list()

    def __iter__(self):
        return iter(self._fields)

    def __setitem__(self, key, value):
        self._fields[key] = value

    def __getitem__(self, item):
        return self._fields[item]

    def __len__(self):
        return len(self._fields)

    def append(self, item):
        self._fields.append(item)

    def render(self):
        lines = list()
        lines.append('Defaults:')
        lines.append('---')
        lines.append(self.render_defaults())
        lines.append('Validators:')
        lines.append('---')
        lines.append(self.render_validators())
        return "\n".join(lines)

    def render_defaults(self):
        defaults = dict()
        for field in self:
            defaults[field.name] = field.default
        return yaml.dump(defaults, **YAML_DUMP_KWARGS)

    def render_validators(self):
        validators = list()
        for field in self:
            validators.append(field.render_validators())
        return "\n".join(validators)


class Field(object):

    def __init__(self, name, description=None, default=None, checks=None):
        self.name = name
        self.description = description
        self.default = default
        self.checks = checks if checks is not None else list()

    def render_validators(self):
        lines = list()
        for check in self.checks:
            validator = ValidatorFactory.get_from_data(check)
            lines.append(validator.render(self))
        return '\n'.join(lines)


class ValidatorFactory(object):

    @staticmethod
    def get_from_data(data):
        if 'choices' in data:
            return ChoicesValidator(data['choices'])
        if 'unix_path' == data:
            return UnixPathValidator()


class Validator(object):

    msg = 'Validation error'

    def render(self, field):
        data = [{
            'fail': {
                'msg': self.msg
            },
            'when': self.failed_when(field)
        }]
        return yaml.dump(data, **YAML_DUMP_KWARGS)

    def failed_when(self, field):
        raise NotImplementedError


class UnixPathValidator(Validator):

    msg = 'Value is not an unix path'

    def failed_when(self, field):
        return 'not {name} | dirname'.format(name=field.name)


class ChoicesValidator(Validator):

    def __init__(self, choices):
        self.choices = choices

    @property
    def msg(self):
        return 'Value should be one of "{}"'.format(', '.join(self.choices))

    def failed_when(self, field):
        return '{name} not in ["{choices}"]'.format(name=field.name, choices='", "'.join(self.choices))


class Manager(object):

    def __init__(self, schema_path):
        self.schema_path = schema_path
        self._registry = FieldsRegistry()
        self._generate_registry()

    def get_validation(self):
        return self._registry.render()

    def _generate_registry(self):
        self._load_schema()
        for key, value in self.schema.iteritems():
            self._registry.append(Field(key, **value))

    def _load_schema(self):
        with open(self.schema_path) as schema_file:
            self.schema = yaml.load(schema_file)

    def render(self):
        return self._registry.render()
