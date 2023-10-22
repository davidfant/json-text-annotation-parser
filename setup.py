from setuptools import setup, find_packages

setup(
  name="json_text_annotation_parser",
  version="0.0.1",
  author="David Fant",
  author_email="david@fant.io",
  description="A Python library for parsing text annotations of JSON documents and converting that to annotated paths in the JSON document.",
  long_description=open("README.md", "r").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/davidfant/json-text-annotation-parser",
  packages=find_packages(),
  python_requires='>=3.10',
)
