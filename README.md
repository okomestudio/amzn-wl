# amzn_wl

`amzn-wl` is a tool to get the pricing information of the products in
Amazon Wish Lists.

Behind the scene, it uses Selenium to sign in and browse the Amazon
website. The tool is intended to replace manual labor of browsing wish
lists regularly to just check out pricing fluctuation (which I was
guilty of doing too much). Therefore, the browsing is intentionally
done slowly. Mass scraping has never been an intention, and such usage
is strongly discouraged. Use at your own risk.

## Install

Create a Python virtual environment, and run

``` shellsession
$ pip install .
```

Also run the database migration (the historical data are saved to
SQLite)

``` shellsession
$ alembic upgrade head
```

## Usage

Simplest way to start the process is to run the command

``` shellsession
$ amzn-wl
```

This will launch a browser session, asks interactively for account
credentials (username, password, and OTP code), and then starts
extracting data. The output will be dumped to a JSON-line file named
`dump.jsonl`. The JSON-line can be processed by a tool like `jq` to
list items in sorted order by price, e.g.,

``` shellsession
$ bin/wl-sort-by-price dump.jsonl
```

The browsing can also be done in the "headless" mode with the
`--headless` option. The output file name can also be provided by the
`--dump` (or `-d`) option:

``` shellsession
$ amzn-wl --headless -d "$output"
```

The account credentials can also be provided via environment variables

``` shellsession
$ AMZN_USERNAME=... AMZN_PASSWORD=... AMZN_OTP=... amzn-wl -d "$output"
```

This may be useful when you use a secret manager and want to
programatically set these credentials.

## TODOs

- Restart and refresh the landing page if the login widge cannot be found
