# Example Configs

This folder includes two examples of configration files that **start.py** will take.
    
    client.json: experiment configuration for the client

    server.json: server configuration 


## Client configration

A JSON file that sets attributes for the experiment:

* *experiment_name*: a string indicating the name of this experiment run, could be used for later analysis.

* *browsers*: a list of tested browsers. This includes their version following the `=` symbol. If no version is supplied (no `=` symbol is found), the current stable version of the browser is tested.

* *pets*: a dictionary where the key is a browser and the value is a list of lists of extensions to test on that browser. That means more extensions can be installed during a single run. Extension name "None" stands for a run with no extensions installed. **Please note that the integration testing works based on comparing values gathered during a run with no extensions installed and runs with extensions installed. A run with the "None" extension must always exist in order to perform integration testing and it must always come first before any other runs in the *pets* list.**

* *delay*: defines how long should the page visit take in seconds.

* *mode*: use `interactive` if you'd like to see the visits happen sqeuntially. Use `threaded` for parallel visits.

* *integration_testing*: a bool value indicating whether integration testing should start right after the data gathering is complete. 

### How to select a browser version
To select a specific browser version, the browser name must be followed by a `=` symbol and the name of the version. For example if tests are to be performed using **Google Chrome version 122** and **Mozilla Firefox version 102**, the list values must be `chrome=122` and `firefox=102`. This is supported by the [Chrome for testing](https://googlechromelabs.github.io/chrome-for-testing/) and [Firefox public releases](https://ftp.mozilla.org/pub/firefox/releases/) directories.
```
    "browsers": ["chrome=122", "firefox=102"],
``` 
**Selenium Manager** also supports browser version names representing the current stage of development, for example `stable`, `beta`, `dev`, `canary` and `esr` for Mozilla Firefox.
```
    "browsers": ["chrome=canary", "firefox=esr", "chrome=122", "firefox=102", "chrome=dev", ...],
``` 

### How to list extensions for testing
To test an extension you must add it to the list inside its individual list. If you'd like to add another extension to the run, you can add it to the list as well. The one big list of lists represents which extension combinations will be tested on given browser.

For example, if you wanted to perform a run using **Google Chrome canary version** with these extension combinations:

- run with no extension installed (mandatory for integration testing),
- *JShelter tested at level 2* and *uBlock Origin*,
- *DuckDuckGo Privacy Essentials*, *JShelter at level 3* and *Ghostery*,
- and *Decentraleyes*

And another run using **Mozilla Firefox esr version** with these extension combinations:
- run with no extension installed (mandatory for integration testing),
- *JShelter tested at level 2* and *Privacy Badger*
- and *Ghostery*

The configuration file must look like this:
```
    "browsers": ["chrome=canary", "firefox=esr"],
    "pets": {
        "chrome=stable":   [ ["None"], ["JS_2", "UO"], ["DDGPE", "JS_3", "Gh"], ["DE"]],
        "firefox=esr": [ ["None"], ["JS_2", "PB"], ["Gh"] ]
        },
```
The extension name abbreviations are defined in a dictionary inside the `start_browser.py` file. They can be changed at any time. New extensions can also be added there. If you are interested in adding a new extension, you must also add an extension file inside the `addon` folder in its respective browser folder. More information can be found inside the `start_browser.py` file. All available extensions and their abbreviation as of now are:

- *JShelter* - `JS_0`, `JS_1`, `JS_2`, `JS_3`, `JS_NBS` or `JS_DLS` (the `JS_DLS` and `JS_NBS` extension settings are mutually exclusive with any other extension)
- *uBlockOrigin* - `UO`
- *Ghostery* - `Gh`
- *Decentraleyes* - `DE`
- *DuckDuckGo Privacy Essentials* - `DDGPE`
- *NetCraft* - `NC`
- *NoScript* - `NS`
- *CanvasBlocker* for *Mozilla Firefox* - `CB`
- *CanvasBlocker* for *Google Chrome* - `CB`
- and *Privacy Badger* - `PB`
- also for a run with no extensions installed - `None` (the `None` extension setting is mutually exclusive with any other extension).

### Special extension configurations
If you are interested in setting an extension to a specific configuration or maybe doing some client-side testing, you can add an underscore after the abbreviation. The parser considers `_` symbol as a seperator. Whatever comes after `_` you can configure in the `start_browser.py` file. For example using `JS_NBS` as a extension name in the JSON file performs client-side tests to check the functionality of user defined behavior through the extension UI. More information can be found inside the `start_browser.py` file.

## Server configuration

A JSON file that includes information for the fingerprinting server, including:

* *fp\_sites*: a list of fingerprinting website URLs to visit. In this case only one site is visited, as it is the only site where we have control over how a fingerprint is gathered and calculated.

* *socks5\_proxy*: a boolean value indicating whether or not to configure socks5 proxy for browsers 

* *proxy_setting*: a dictionary of setting info if using socks5 proxy
