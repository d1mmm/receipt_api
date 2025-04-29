from setuptools import setup, find_packages
from os import path
from pkg_resources import parse_requirements

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def load_requirements(fname: str) -> list:
    requirements = []
    with open(path.join(here, fname), 'r', encoding='utf-8') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(f"{req.name}{extras}{req.specifier}")
    return requirements

setup(
    name='receipt_api',
    version='0.1.0',
    description='FastAPI-based ASYNC REST API for creating and viewing receipts with user auth',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/d1mmm/receipt_api',
    author='Dima Moroz',
    author_email='d1m.moroz007@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: FastAPI',
        'Topic :: Software Development :: APIs',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='fastapi sqlalchemy postgresql jwt receipts api',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.8',
    install_requires=load_requirements('requirements.txt'),
    extras_require={
        'dev': load_requirements('requirements.dev.txt') if path.exists(path.join(here, 'requirements.dev.txt')) else []
    },
    include_package_data=True,
    package_data={
        '': ['requirements.txt', 'requirements.dev.txt'],
    },
    entry_points={
        'console_scripts': [
            "receipt-api=app.main:run",
        ],
    },
)
