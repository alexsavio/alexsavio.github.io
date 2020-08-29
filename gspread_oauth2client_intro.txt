Title: Access Google Spreadsheets using gspread and OAuth2Client
Date: 2015-05-14 19:11:46
Modified: 2016-03-29 13:30:00
Category: Python
Tags: python, gspread, google, authentication
Slug: gspread_oauth2client_intro
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: How to access Google spreadsheets using the Python module gspread and the OAuth2Client authorization system.


Jump to [the Materials and Methods section](#materials) if you don't want to read the introduction.

This post presents a way of accessing Google Spreadsheets(GS) and securely distributing Python source code that  uses GS.

## Introduction

[Google spreadsheets](https://docs.google.com/spreadsheets/)(GS) are useful for fast deployment of simple
forms on the web as well as share and collaborate on simple data structures with other people.

Not everybody has enough experience with the sheet cell functionalities and the small devils of the spreadsheet world. You may find yourself trapped on the [Google Docs help](https://support.google.com/docs) or looking for that non-existent function in the [GS reference](https://support.google.com/docs/table/25273?hl=en) trying to program more complex data processes. In those cases I feel the urge to unleash the power of Python over the data.

There are ways of doing that through the Official Google Spreasheet API. The API is flexible but can take a considerable amount of work if your idea is "just" accessing the data of the spreadsheets and doing a few operations on them.

To leverage all the API work and help us all there is [gspread](https://github.com/burnash/gspread), which wraps up the API and makes clear and pragmatic functions sprout.

### How to authenticate through gspread

Initially the authentication method to use gpsread was using username and password pair. This is a problem when you need to share your application with other people. You can't share your passwords, create user accounts for every user of your application or even, you would have to share your common document to every user you have.

In these situations ideally your application should prove its own identity to the API, but no user consent should be necessary. Similarly, in enterprise scenarios, your application could request delegated access to some resources. This is a possible scenario where OAuth2.0 comes to save you.

### OAuth2.0 authorization framework

The [OAuth2.0 authorization framework](http://en.wikipedia.org/wiki/OAuth) is being adopted by many web services as a secure way for 3rd-parties to deploy software that use their APIs. It is well summarized [here](https://developers.google.com/identity/protocols/OAuth2#serviceaccount).

As the [OAuth2.0 RFC](http://tools.ietf.org/html/rfc6749) says:

*The OAuth 2.0 authorization framework enables a third-party
application to obtain limited access to an HTTP service, either on
behalf of a resource owner by orchestrating an approval interaction
between the resource owner and the HTTP service, or by allowing the
third-party application to obtain access on its own behalf.  This
specification replaces and obsoletes the OAuth 1.0 protocol described
in RFC 5849.*

[Google has adopted OAuth 2.0](https://developers.google.com/identity/protocols/OAuth2) for his APIs and web services. They also created a Python module for accessing resources protected by OAuth 2.0 called [oauth2client](https://github.com/google/oauth2client).

Check [here](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) to understand more how the authorization process works or how you can use it.

## Materials and Methods<a id="materials"></a>

### Installation

The simplest tool to install the needed modules is `pip`:

    pip install gspread oauth2client

Following the [note](#install-crypto), you would also want to install `pycrypto` or `pyopenssl`, e.g.:

    pip install pycrypto

### Experiment

### Create signed JSON Web Tokens (JWTs)

The gspread documentation explains how to create Google OAuth2.0 JSON Web Tokens (JWTs) [here](http://gspread.readthedocs.org/en/latest/oauth2.html).

Follow his full instructions on the [Google Developers Console](https://console.developers.google.com/project) web site to create a service account Client ID JSON file. I will call the file `gspread-test.json` from now on.

After saving `gspread-test.json` you need to **share your document with the given email in the `client_email` field** of the file. Otherwise you’ll get a `SpreadsheetNotFound` exception when trying to open it.

**Note**: The resulting JSON file is a secure authorization key for any spreadsheet you may want to. For this reason you should hide this file should as it could be used to do nasty things against your spreadsheets. Please follow more comments on this in the [discussion](#discussion) section.

### Sign your JWTs for credentials

This is a snippet of how to obtain the data of a spreadsheet given its name in the variable `wks`.

    ```python
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    json_key = 'gspread-test.json'
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_api_key_file, scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("Where is the money Lebowski?").sheet1
    ```

The `gc` object is a `gspread.client.Client`, check its main functionality [here](http://gspread.readthedocs.org/en/latest/index.html#main-interface).

 You can find [here](http://gspread.readthedocs.org/en/latest/index.html#models) the main functionality of `wks` is a GS class.

<a id="install-crypto"></a>
**Note:** You must create the signed credentials using `ServiceAccountCredentials` from `oauth2client.service_account`.
This class requires either `PyOpenSSL`, or `PyCrypto 2.6` or later. If you are getting `CryptoUnavailableError` when trying to create your signed credentials, install [PyOpenSSL](https://github.com/pyca/pyopenssl) or [PyCrypto](https://github.com/dlitz/pycrypto), e.g.:

    pip install pycrypto

### Results

Have a look at the possibilities you have with gspread [here](https://github.com/burnash/gspread#more-examples).

Some examples here:

#### Opening a Spreadsheet

    ```python
    # You can open a spreadsheet by its title as it appears in Google Docs
    sh = gc.open("My poor gym results") # <-- Look ma, no keys!

    # If you want to be specific, use a key (which you can extract from
    # the spreadsheet's url)
    sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

    # Or, if you feel lazy to extract that key, paste the entire url
    sht2 = gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
    ```

#### Selecting a worksheet

    ```python
    # Select worksheet by index. Worksheet indexes start from zero
    worksheet = sh.get_worksheet(0)

    # By title
    worksheet = sh.worksheet("January")

    # Most common case: Sheet1
    worksheet = sh.sheet1

    # Get a list of all worksheets
    worksheet_list = sh.worksheets()
    ```

#### Creating a worksheet

    ```python
    worksheet = wks.add_worksheet(title="A worksheet", rows="100", cols="20")
    ```

#### Getting a cell value

    ```python
    # With label
    val = worksheet.acell('B1').value

    # With coords
    val = worksheet.cell(1, 2).value
    ```

#### Getting all values from a worksheet as a list of lists

    ```python
    list_of_lists = worksheet.get_all_values()
    ```

### Discussion<a id="discussion"></a>

Regarding security issues, it is not clear to me how we should 'hide' the JSON key information in case we needed to distribute the Python applications created. In a compiled language it would be possible to put the content in a file, obfuscate it, encrypt it and then compile it. Of course we could do this on Python using, for instance, Cython, but I would like something simpler and I think there isn't one.
*If you have any suggestion on how to do this in a pure Python package, please send me an email.*

### Links

1. <https://docs.google.com/spreadsheets/>

2. <https://support.google.com/docs>

3. <https://support.google.com/docs/table/25273?hl=en>

4. <https://github.com/burnash/gspread>

5. <http://en.wikipedia.org/wiki/OAuth>

6. <https://developers.google.com/identity/protocols/OAuth2#serviceaccount>

7. <http://tools.ietf.org/html/rfc6749>

8. <https://developers.google.com/identity/protocols/OAuth2>

9. <https://github.com/google/oauth2client>

10. <https://developers.google.com/identity/protocols/OAuth2ServiceAccount>

11. <http://gspread.readthedocs.org/en/latest/oauth2.html>

12. <https://console.developers.google.com/project>

13. <http://gspread.readthedocs.org/en/latest/index.html#main-interface>

14. <http://gspread.readthedocs.org/en/latest/index.html#models>

15. <https://github.com/pyca/pyopenssl>

16. <https://github.com/dlitz/pycrypto>

17. <https://github.com/burnash/gspread#more-examples>
