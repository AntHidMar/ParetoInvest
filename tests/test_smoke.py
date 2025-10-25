import sys
import os

# Añadir la raíz del proyecto al PYTHONPATH para que los imports funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import_package():
    import ParetoInvest  # usar el nombre real de la carpeta

def test_import_main():
    from ParetoInvest import main

def test_main_entrypoint():
    try:
        from ParetoInvest import main
        # Solo comprobar que la función main es callable, no se ejecuta
        assert callable(main.main)
    except Exception as e:
        assert False, f"Main entry point is not callable: {e}"



"""
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
"""