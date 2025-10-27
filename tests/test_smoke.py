import sys
import os
import pytest

# Añadir la raíz del proyecto al PYTHONPATH para que los imports funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import_package():
    import ParetoInvest  # usar el nombre real de la carpeta

def test_import_main():
    from ParetoInvest import main

"""def test_main_entrypoint():
    try:
        from ParetoInvest import main
        # Solo comprobar que la función main es callable, no se ejecuta
        assert callable(main.main)
    except Exception as e:
        assert False, f"Main entry point is not callable: {e}" """


def test_main_entrypoint():
    try:
        from ParetoInvest import main
        assert callable(main.main)
    except ModuleNotFoundError as e:
        if "PyQt5" in str(e):
            pytest.skip("Skipping GUI tests because PyQt5 is not available")
        else:
            raise
    except Exception as e:
        pytest.fail(f"Main entry point is not callable: {e}")