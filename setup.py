from setuptools import setup, find_packages

setup(
    name="goodfire_webapp",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'goodfire_webapp': [
            'static/*',
            'templates/*',
        ],
    },
    install_requires=[
        'Flask',
        'goodfire',
        'python-dotenv',
        'gunicorn',
    ],
) 