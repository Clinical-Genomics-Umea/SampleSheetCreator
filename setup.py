from distutils.core import setup
import py2exe

setup(
    console=["main_window.py"],
    requires=["pandas", "PyQt5", "numpy", "PyYAML", "packaging", "jinja2", "schema"],
)
