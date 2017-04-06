# Dunya front end

[![Build Status](https://travis-ci.org/giuband/dunya-frontend.svg?branch=master)](https://travis-ci.org/giuband/dunya-frontend)
![Dependencies](https://david-dm.org/giuband/dunya-frontend.svg)

## Development
First use
```
npm install
```
to install all the dependencies.

If you want to generate the production build, run:
```
npm run build
```

If instead you want to start an express server that simulates the client-only environment with hot reloading, run:
```
npm run dev
```


## Integration with back-end
The web-app is written to be flexible to the content provided by the server. To let this application know which catalogue to load, **start by rendering `index.html` with a template variable named `dunya_catalogue`**, whose value must be in `[carnatic, hindustani]` (although it's possible to extend these values, see section [Customization/Adding new content](#customizationadding-new-content)).

### Settings and behavior
All settings in the following paragraphs are stored in the file `src/settings.js`. If you change one, please rebuild the bundle with the command `npm run build`.

### Serving data for filters
At initial mount, the app requests data from the server to fill up the sidebar with filters. The address for this request is the value of the setting `FILTERS_DATA_URL[$dunya_catalogue]`, where `$dunya_catalogue` is the content of the template variable `dunya_catalogue` passed to `index.html` (as explained in previous section). The response of the server at this address must be an object, whose values are arrays of entries for the corresponding key. An example:
```javascript
{
  "artists": [
    {
      "id": "a1",
      "name": "artist 1",
      "instruments": ["i1", "i2"]
    }, {
      "id": "a2",
      "name": "artist 2",
      "instruments": []
    }, // ...other artists
  ],
  "concerts": [
    {
      "id": "c1",
      "name": "concert 1",
      "aliases": ["that concert"]
    }, {
      "id": "c2",
      "name": "concert 2"
    }, // ...other concerts
  ],
  "instruments": [
    {
      "uuid": "i1",
      "name": "Violin"
    }, {
      "uuid": "i2",
      "name": "Cello"
    }, // ...other instruments
  ], // ...other keys
}
```
**The key `artists` in the response is mandatory**. There are no other rules for the names and/or amount of the response keys. Each key of the response will be a section of filters in the sidebar.

**Each entry of each field** (the fields in this example are `artists, concerts, instruments`) **must have a `name` property**.
Each entry must as well contain an id field, but *this is not required to be named* `id`; edit the setting `ID_KEYS` to list all the possible keys for the id field and the app will automatically detect which entry key corresponds to the entry id. If an entry of a specific field has a key that is a reference to the ids of another field (in the example, the first entry of `artists` has a reference to `instruments`, i.e. it contains the list of instruments played by that artist), that reference will be used for advanced content filtering. In this case, if the user selected the instrument 'Violin', only "artist 1" would appear in the `artists` section as he's the only one playing the violin. On the other hand, the content of the `concerts` field wouldn't be affected as its entries don't have a reference to the `instruments` fields.

If an entry has an `aliases` field, the values on that field will be used during the search.

### Serving data for autocomplete
You might want to send data for autocomplete when the user is typing in the search bar. In this case, start by setting the proper address in `AUTOCOMPLETE_URL[$dunya_catalogue]`. This address should then read the parameter `input` from the incoming request and reply to it with a list of results, in the following shape:
```javascript
[
  {
    "mbid": "8618ff0c-555e-4f3c-90d5-0438aeae4659",
    "name": "Balagopala",
    "category": "Concerts",
    "matchFor": "balagopala"
  }, {
    "mbid": "33ef2098-d4ba-40ec-b972-dbda5114e3e2",
    "name": "Koovi Azhaithal",
    "category": "Artists",
    "matchFor": "koovi"
  }, // ... other results
]
```
**Each result must have an id and the `name`, `category` properties.** The field `matchFor` is optional but highly recommended, and stands for the substring of the search input that matches the given result. In the example above, for instance, the input in the search bar could have been `"balagopala koovi"`: if the user clicks on the first recommended item, the concert `"Balagopala"` will be added to the selection list, while the search input will be transformed to `"koovi"`.

If you don't want to enable autocomplete, just don't set the option `AUTOCOMPLETE_URL[$dunya_catalogue]` (or put it to `undefined`).

### Serving search results
The client will send a request informing the server of the selected filters together with the text input in the search bar. An example:
```
?recording=rec&artists=artist1ID+artist2ID&instruments=instrument1ID
```

The server answers this request with a response that is a list of object, each one storing the details of a recording the matches the search. **Each result should then have the following keys: `concert`, `image`, `linkToRecording`, `mainArtists`, `name`**.
The following one is an example of a correct response:
```javascript
[
  {
    "collaborators": [ // list of collaborators (this key can be omitted if no collaborators are available)
      {
        "name": "artist 1", // name of the first collaborator
        "instrument": "voice" // and the instrument he/she plays in this recording
      }, // ... other collaborators
    ],
    "concert": "concert 1", // the concert name
    "image": "/static/image.png",
    "linkToRecording": "/recording/1.html", // link to the recording page
    "mainArtists": ["artist 1", "artist 2"], // the names of the main artists of the recording
    "name": "recording 1", // the name of the recording
    "taala": "aadi", // optional
    // ... other optional keys (such as "raaga", "form",... No fixed key names here, use what you want!)
  }, // ... other search results, with the same shape
]
```
The client makes no assumption on the keys other than `concert`, `image`, `linkToRecording`, `mainArtists`, `name` and `collaborators`. If the response contain any other key, the value for that key will be displayed in the final UI. This means that the UI will correctly work with non-carnatic results without any change in the code.

The search endpoint should return:
```javascript
{
  "result": [ // The results in the format described above
  ],
  "moreResults": // Link to get more results
}
```

## User session information
The UI changes whether the user is logged in or not. When rendering the template `index.html`, the server should use the template tag `user_name` whose value is the username of the current user. If the user is not logged in, it should be an empty string. Moreover, the settings `LOGIN_URL`, `LOGOUT_URL` and `USER_PROFILE_BASE_URL` have to be customized. The user profile url is intended to be in the shape `USER_PROFILE_BASE_URL/{userName}`.

## Customization/Adding new content
In case of extending the application to support a new catalogue, the settings for the new catalogue have to be added in:
- `FILTERS_DATA_URL`
- `SEARCH_URL`
- `AUTOCOMPLETE_URL`

`SELF_EXPLANATORY_CATEGORY_ITEMS` might as well be extended in order to include new response keys that don't need an explanation on the search bar. In the same way, you might need to add new items to the list `ID_KEYS`.

### Singular/Plural rules
Edit the file `utils/pluralRules.js` to add new rules for singular and plural. Since the server mostly returns keys in the plural form, you should only need to add rules for singular forms.

## License
MIT
