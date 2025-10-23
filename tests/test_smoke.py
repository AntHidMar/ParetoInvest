def test_import_package():
    import paretoinvest

def test_import_main():
    from paretoinvest import main

# Optionally, check that the main entry point can be called without crashing
# (if it does not require arguments or GUI interaction)
def test_main_entrypoint():
    try:
        from paretoinvest import main
        # Only check import and callable, not actual execution
        assert callable(main.main)
    except Exception as e:
        assert False, f"Main entry point is not callable: {e}"
