from fields import Manager


manager = Manager('tests/test-schema.yml')
print manager.render()
