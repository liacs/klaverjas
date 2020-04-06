from setuptools import find_packages, setup


setup(
    name='klaverjas',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    zip_safe=False,
    install_requires=[
        'eventlet',
        'Flask-Bootstrap',
        'Flask-Login',
        'Flask-SocketIO',
        'Flask-SQLAlchemy',
        'Flask-WTF',
    ])
