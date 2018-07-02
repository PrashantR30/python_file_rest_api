from setuptools import setup

setup(
    name='Brownie',
    version='0.1',
    long_description=__doc__,
    scripts=['app.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)
