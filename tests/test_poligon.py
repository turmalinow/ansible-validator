import yaml
from nose.tools import assert_is_instance, assert_equals

from fields import Manager


def test__load_dict():
    with open('test-schema.yml') as schemafile:
        schema = yaml.load(schemafile)

    assert_is_instance(schema, dict)


def test__manager():
    manager = Manager('test-schema.yml')

    assert_equals(len(manager._registry), 4)
