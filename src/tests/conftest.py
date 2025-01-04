def pytest_collection_modifyitems(items):
    siftfile_constructor_tests = [item for item in items if "TestSiftFileConstructor" in item.nodeid]
    if siftfile_constructor_tests:
        print("\n=========== SiftFile Constructor Testing ===========")
