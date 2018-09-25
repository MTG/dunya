# Dunya REST API

Dunya provides an API for programatic access to the metadata
and files stored in the platform.

## Authentication

You must authenticate in order to access API resources. Do this by sending a header

    Authorization: Token <token>

with your request. You can get the token on your dunya profile page at
https://dunya.compmusic.upf.edu/user/profile/

## Python client

A Python client to access the Dunya API is available as part of the 
[pycompmusic](https://github.com/MTG/pycompmusic/) package.
You can find documentation for this package at
https://dunya.compmusic.upf.edu/docs/

## API List

Each of the APIs that are provided in dunya are explained in the following linked documents

* [docserver/API_README.md](docserver/API_README.md)
* [carnatic/API_README.md](carnatic/API_README.md)