Carnatic API
============

This document describes the API to access information about the Carnatic data
in Dunya.

Other APIs
----------
See also documentation for the docserver API in `docserver/API_README.md`

Authentication
--------------
You must authenticate in order to access API resources. Do this by sending a header

    Authorization: Token <token>

with your request. You can get the token on your dunya profile page at
https://dunya.compmusic.upf.edu/user/profile/

Methods
-------

The plural methods return 100 items at a time, wrapped in a paged structure
like this:

    {
        "count": 1068,
        "next": "http://absolute-url-to?page=2",
        "previous": null,
        "results": [ ... ]
    }

To get all items in the database you must repeatedly call the `next` url until
it is `null`.

**Artists:** ``http://dunya.compmusic.upf.edu/api/carnatic/artist``
Lists all carnatic artists.

    "results": [
        {
            "mbid": "4d024ce6-f697-448e-be8a-c31caffdf068",
            "name": "T.N. Krishnan"
        },
        {
            "mbid": "39c1d741-6154-418b-bf4b-12c77ba13873",
            "name": "Srimushnam V Raja Rao"
        },
    ]

**Artist:** ``http://dunya.compmusic.upf.edu/api/carnatic/artist/[artistid]``
Show details for a single artist.

    {
    "mbid": "4d024ce6-f697-448e-be8a-c31caffdf068",
    "name": "T.N. Krishnan",
    "concerts": [ {
            "mbid": "d89a53a7-ad04-4608-9328-9de2d38dae85",
            "title": "Carnatic Instrumental - Violin"
    } ],
    "instruments": {
        "id": 2,
        "name": "Violin"
    },
    "recordings": [ {
            "mbid": "f4b9e94f-7459-4c98-85bd-be1e6823332f",
            "title": "Shri Satyanarayanam"
    }, ]
    }

**Concerts:** ``http://dunya.compmusic.upf.edu/api/carnatic/concert``
List all carnatic concerts

    "results": [
        {
            "mbid": "54ab1640-8479-4b7e-bb35-b40c30176501",
            "title": "Carnatic Vocal (1910 - 1965)"
        },
    ]

**Concert:** ``http://dunya.compmusic.upf.edu/api/carnatic/concert/[concertid]``
Show details for a single concert

    {
        "mbid": "54ab1640-8479-4b7e-bb35-b40c30176501",
        "title": "Carnatic Vocal (1910 - 1965)",
        "year": 1994,
        "recordings": [
            {
                "mbid": "b9c77de4-0618-4106-8930-b01b9c602294",
                "title": "Kalala Nerchina",
            }
        ],
        "artists": [  # Artists who perform on the release
            {
                "mbid": "6110a180-48ae-42f3-9220-85a1eda5d85d",
                "name": "T. S. Balasubramaniam",
                "instrument": "Vocal"
            },
            {
                "mbid": "1038a7f3-eda5-43a6-8366-e07085fbd14b",
                "name": "Umayalpuram N. Kodandarama Iyer",
                "instrument": "Ghatam"
            },
        ],
        "concert_artists": [ # The 'main' artist who the release is by
            {
                "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85",
                "name": "G. N. Balasubramaniam"
            }
        ]
    }

**Recordings:** ``http://dunya.compmusic.upf.edu/api/carnatic/recording``
List all carnatic recordings

    "results": [
        {
            "mbid": "f60ab9a4-c1bd-411f-8f64-52915bb5fbb7",
            "title": "Evarani"
        },
    ]

**Recording:** ``http://dunya.compmusic.upf.edu/api/carnatic/recording/[recid]``
Show details for a single recording

    {
        "mbid": "902b21c0-985b-4b6b-a30e-c3c505b69fb1",
        "title": "Margazhi Thingal",
        "artists": [
            {
                "mbid": "0afc280e-c99c-4ab7-99d6-d1757c85d0f9",
                "name": "Sumithra Vasudev"
            }
        ],
        "raaga": {
            "id": 266,
            "name": "N\u0101\u1e6da"
        },
        "taala": {
            "id": 1,
            "name": "\u0100di"
        },
        "work": {
            "mbid": "95d1df67-6698-43ff-90ae-b01ac876a100",
            "title": "Margazhi Thingal"
        },
        "concert": {
            "mbid": "d6f4d5ca-df12-4d4f-a16b-ca4a1bf80ab0",
            "title": "December Season 2011"
        }
    }


**Works:** ``http://dunya.compmusic.upf.edu/api/carnatic/work``
List all carnatic works

    "results": [
        {
            "mbid": "419e17f2-890b-4151-9cd3-0307869c0a39",
            "title": "Mayatita Swaroopini"
        },
    ]

**Work:** ``http://dunya.compmusic.upf.edu/api/carnatic/work/[workid]``
Show details for a single work

    {
        "mbid": "419e17f2-890b-4151-9cd3-0307869c0a39",
        "title": "Mayatita Swaroopini",
        "composers": [
            {
                "mbid": "5d7336f5-cb04-46eb-bdfc-64d8fe976931",
                "name": "Ponnayya Bhagavathar"
            }
        ],
        "raagas": [
            {
                "id": 72,
                "name": "M\u0101y\u0101m\u0101\u1e37avagau\u1e37a"
            }
        ],
        "taalas": [
            {
                "id": 2,
                "name": "R\u016bpaka"
            }
        ],
        "recordings": [
            {
                "mbid": "88166f7e-a85d-4c7a-91ec-2f16831b7e79",
                "title": "Maya Tita Swaroopini"
            }
        ]
}


**Taalas:** ``http://dunya.compmusic.upf.edu/api/carnatic/taala``
List all carnatic taalas

    "results": [
        {
            "id": 1,
            "name": "\u0100di"
        },
    ]


**Taala:** ``http://dunya.compmusic.upf.edu/api/carnatic/taala/[taalaid]``
Show details for a single taala. The argument is a numeric id (from the list)

    {
        "id": 1,
        "name": "\u0100di",
        "common_name": "adi",
        "artists": [
            {
                "mbid": "ea284751-0153-433d-82db-25c22306daf1",
                "name": "Sikkil Gurucharan"
            },
        ],
        "works": [
            {
                "mbid": "7e14309b-cfd7-4a03-bb9e-6df7d7aef587",
                "title": "Nannu Palimpa"
            },
        ]
    }


**Raagas:** ``http://dunya.compmusic.upf.edu/api/carnatic/raaga``
List all carnatic raagas

    "results": [
        {
            "id": 192,
            "name": "C\u0101y\u0101n\u0101\u1e6da"
        },
    ]

**Raaga:** ``http://dunya.compmusic.upf.edu/api/carnatic/raaga/[raagaid]``
Show details for a single raaga. The argument is a numeric id (from the list)

    {
        "id": 2,
        "name": "\u0100bh\u014dgi",
        "common_name": "abhogi",
        "artists": [
            {
                "mbid": "beab6365-8162-4c64-8922-64702cea3227",
                "name": "Sanjay Subrahmanyan"
            },
        ],
        "works": [
            {
                "mbid": "c8bc23f8-3809-48d5-8e00-b654ecc4528a",
                "title": "Sabhapathi"
            },
        ]
    }

**Instruments:** ``http://dunya.compmusic.upf.edu/api/carnatic/instrument``
List all carnatic instruments

    "results": [
        {
            "id": 2,
            "name": "Violin"
        },
    }

**Instrument:** ``http://dunya.compmusic.upf.edu/api/carnatic/instrument/[instid]``
Show details for a single instrument. The argument is a numeric id (from the list)

    {
        "id": 3,
        "name": "Mridangam",
        "artists": [
            {
                "mbid": "c7039633-3631-46f1-a9d0-b1c2b0053343",
                "name": "Anantha R Krishnan"
            },
        ]
    }
