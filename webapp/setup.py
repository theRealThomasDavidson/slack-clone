from setuptools import setup, find_packages

setup(
    name="chat-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "pytest",
        "httpx",
        "pytest-asyncio",
    ],
) 