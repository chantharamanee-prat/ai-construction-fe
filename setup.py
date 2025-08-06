from setuptools import setup, find_packages

setup(
    name="yolo-server",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.109.1",
        "uvicorn==0.27.0",
        "python-multipart==0.0.6",
        "pydantic==2.6.4"
    ],
)
