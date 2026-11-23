# python-i18n [![Build Status](https://github.com/danhper/python-i18n/actions/workflows/ci.yml/badge.svg)](https://github.com/danhper/python-i18n/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/danhper/python-i18n/badge.svg?branch=master)](https://coveralls.io/github/danhper/python-i18n?branch=master) [![Code Climate](https://codeclimate.com/github/danhper/python-i18n/badges/gpa.svg)](https://codeclimate.com/github/danhper/python-i18n)

This library provides i18n functionality for Python 3 out of the box. The usage is mostly based on Rails i18n library.

## Installation

Just run

    python -m pip install python-i18n

If you want to use YAML to store your translations, use

    python -m pip install "python-i18n[YAML]"

Keep the quotes around the extra: shells such as zsh otherwise interpret the
square brackets as a filename pattern and may report `no matches found`.
Use the same Python interpreter that runs your application, including in CI.

If loading a `.yml` or `.yaml` file raises `no loader available for extension`,
check that this interpreter can import PyYAML:

    python -c "import yaml; print(yaml.__version__)"

If the import fails, install the YAML extra with the command above. Restart any
running application afterward, because available loaders are selected when
`i18n` is imported. Renaming a file from `.yml` to `.yaml` does not supply the
missing dependency; both extensions use the same loader.

## Usage

### Basic usage

The simplest, though not very useful usage would be

    import i18n
    i18n.add_translation('foo', 'bar')
    i18n.t('foo') # bar

### Using translation files

YAML and JSON formats are supported to store translations. With the default configuration, if you have the following `foo.en.yml` file

    en:
      hi: Hello world !

in `/path/to/translations` folder, you simply need to add the folder to the translations path.

    import i18n
    i18n.load_path.append('/path/to/translations')
    i18n.t('foo.hi') # Hello world !

Please note that YAML format is used as default file format if you have `yaml` module installed.
If both `yaml` and `json` modules available and you want to use JSON to store translations, explicitly specify that: `i18n.set('file_format', 'json')`

### Translation files inside Python packages

Add an importable package name to `load_package_path` to read JSON or YAML
translations with `importlib.resources.files()`:

    import i18n
    i18n.config.set('file_format', 'json')
    i18n.load_package_path.append('my_app.translations')
    i18n.t('greetings.hello', locale='en')

For example, package `my_app.translations` can contain
`greetings.en.json` with `{"en": {"hello": "Hello"}}`. Include the
translation files as package data when building your distribution.
Resources work in filesystem packages and ZIP-imported packages without
extracting their contents to temporary files.

Filename formats, directory namespaces, locale roots, encoding and memoization
work as for filesystem translations. Package roots are searched after
`load_path`, in list order; later sources can replace earlier translations.
The built-in JSON and YAML loaders support package resources. Custom
text loaders can inherit from `i18n.loaders.loader.Loader`; Python-module
translation files are not supported through `load_package_path`.

### File encoding

Translation files are read as UTF-8 by default. Save JSON and YAML files as UTF-8
in your editor; accented characters such as `é` can appear directly in a UTF-8
file. JSON's `\u00e9` escape represents the same character.

An error such as `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9` usually
means the file was saved in another encoding, rather than that translated text
must be ASCII. If you must use a known legacy encoding, configure it **before
loading any translations**:

```python
import i18n
from i18n import config

config.set('encoding', 'cp1252')  # Use the actual encoding of your files.
config.set('file_format', 'json')
i18n.load_path.append('/path/to/translations')
print(i18n.t('messages.nomF'))  # Fichiers supervisés enregistrés
```

This setting applies to all files the loaders read; it does not auto-detect
encodings. Converting mixed-encoding files to UTF-8 avoids changing the setting
between loads. Already loaded translations and memoized file contents are not
re-decoded when the setting changes, so restart the application after converting
the files or changing its encoding configuration.

### Loading translations at startup

Files are normally loaded when a translation is first requested. To move that
disk access to application startup, load the configured locales explicitly:

```python
import i18n
from i18n import config

i18n.load_path.append('/path/to/translations')
config.set('available_locales', ['en', 'fr'])
i18n.load_all()
```

`load_all()` reads matching files recursively under every configured load path,
preserving file and directory namespaces and the active locale. It uses the
configured `filename_format`, `file_format` and encoding. You can instead pass
`i18n.load_all(['fr'])` to load only selected locales. Missing directories and
invalid translation files raise their usual loader errors during startup.

Subsequent lookups of loaded keys use the translation container. Missing keys
still follow the normal search and fallback behavior; preloading does not cache
missing translations or watch files for changes.

### Memoization

Setting the configuration value `enable_memoization` in the settings dir will load the files from disk the first time they
are loaded and then store their content in memory. On the next use the file content will be provided from memory and not
loaded from disk, preventing disk access. While this can be useful in some contexts, keep in mind there is no current way of
issuing a command to the reloader to re-read the files from disk, so if you are updating your translation file without restarting
the interpreter do not use this option.

### Namespaces

#### File namespaces

In the above example, the translation key is `foo.hi` and not just `hi`. This is because the translation filename format is by default `{namespace}.{locale}.{format}`, so the {namespace} part of the file is used as translation.

To remove `{namespace}` from filename format please change the `filename_format` configuration.

    i18n.set('filename_format', '{locale}.{format}')


#### Directory namespaces

If your files are in subfolders, the foldernames are also used as namespaces, so for example if your translation root path is `/path/to/translations` and you have the file `/path/to/translations/my/app/name/foo.en.yml`, the translation namespace for the file will be `my.app.name` and the file keys will therefore be accessible from `my.app.name.foo.my_key`.

## Functionalities

### Finding keys from translated text

There is no inverse `t()` operation: several keys can have the same text, and
pluralization, placeholders and fallback can produce additional results. For an
exact lookup of stored strings in one locale, build an index from the loaded
translations. Keep a list of keys for each text so duplicate values are retained.

For example, with `messages.de_DE.yml`:

```yaml
de_DE:
  hello: Hallo
  greeting: Hallo
```

```python
from collections import defaultdict
from i18n import resource_loader, translations

locale = 'de_DE'
resource_loader.load_translation_file(
    'messages.de_DE.yml', '/path/to/translations', locale=locale
)
keys_by_text = defaultdict(list)
for key, value in translations.container.get(locale, {}).items():
    if isinstance(value, str):
        keys_by_text[value].append(key)

assert keys_by_text.get('Hallo', []) == ['messages.hello', 'messages.greeting']
assert keys_by_text.get('Unknown', []) == []
```

Files are loaded lazily by `t()`, so `translations.container` contains only the
translations already loaded or added with `add_translation`. Explicitly load each
file you want to include before building the index. Its keys retain their
namespaces; it does not search fallback locales or format placeholders. Non-string
values (such as plural dictionaries and arrays) are omitted. Read the container
without changing it, and rebuild the index after adding or reloading translations.

### Placeholder

You can of course use placeholders in your translations. With the default configuration, the placeholders are used by inserting `%{placeholder_name}` in the ntranslation string. Here is a sample usage.

    i18n.add_translation('hi', 'Hello %{name} !')
    i18n.t('hi', name='Bob') # Hello Bob !

### Pluralization

Pluralization is based on Rail i18n module. By passing a `count` variable to your translation, it will be pluralized. The translation value should be a dictionnary with at least the keys `one` and `many`. You can add a `zero` or `few` key when needed, if it is not present `many` will be used instead. Here is a sample usage.

    i18n.add_translation('mail_number', {
        'zero': 'You do not have any mail.',
        'one': 'You have a new mail.',
        'few': 'You only have %{count} mails.',
        'many': 'You have %{count} new mails.'
    })
    i18n.t('mail_number', count=0) # You do not have any mail.
    i18n.t('mail_number', count=1) # You have a new mail.
    i18n.t('mail_number', count=3) # You only have 3 new mails.
    i18n.t('mail_number', count=12) # You have 12 new mails.

### Lists

A translation value can be a list. `t()` then returns a list, with placeholders
filled in every string item. When you pass `count`, plural dictionaries inside
the list are pluralized; without `count` they are returned unchanged. Nested
lists are handled the same way, and other values (numbers, `null`) are returned
as they are. For example, with `foo.en.yml`:

```yaml
en:
  months:
    - January
    - February
  welcome:
    - one: A new user just joined!
      many: "%{count} new users just joined!"
    - Hello %{user}
```

```python
i18n.t('foo.months')[1]                    # February
i18n.t('foo.welcome', count=3, user='Bob') # ['3 new users just joined!', 'Hello Bob']
```

### Fallback

You can set a fallback which will be used when the key is not found in the default locale.

    i18n.set('locale', 'jp')
    i18n.set('fallback', 'en')
    i18n.add_translation('foo', 'bar', locale='en')
    i18n.t('foo') # bar

### Skip locale from root

Sometimes i18n structure file came from another project or not contains root element with locale eg. `en` name.

    {
        "foo": "FooBar"
    }

However we would like to use this i18n .json file in our Python sub-project or micro service as base file for translations.
`python-i18n` has special configuration tha is skipping locale eg. `en` root data element from the file.

    i18n.set('skip_locale_root_data', True)
