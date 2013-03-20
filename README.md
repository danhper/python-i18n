# python-i18n

This library provides i18n functionality for python3 out of the box. The usage is mostly based on Rails i18n library.

## Installation

Simply download the package and run

    python setup.py install

Make sure you are using python3.

## Usage
### Basic usage

The simplest, though not very useful usage would be

    import i18n
    i18n.add_translation('foo', 'bar')
    i18n.t('foo') # bar

### Using translation files

YAML and JSON formats are supported to store translations. Using the default configuration, if you have the following `foo.en.yml` file

    en:
      hi: Hello world !

in `/path/to/translations` folder, you simply need to add the folder to the translations path.

    import i18n
    i18n.load_path.append('/path/to/translations')
    i18n.t('hi') # Hello world !

The translation file name format is by default `{namespace}.{locale}.{format}`.
If your files are in subfolders, the foldernames are also used as namespaces, so for example if your translation root path is `/path/to/translations` and you have the file `/path/to/translations/my/app/name/foo.en.yml`, the translation namespace for the file content will be `my.app.name`.

## Funcionalities
### Placeholder

You can of course use placeholders in your translations. With the default configuration, the placeholders are used by inserting `%{placeholder_name}` in the ntranslation string. Here is a sample usage.

    i18n.add_translation('hi', 'Hello %{name} !')
    i18n.t('hi', name='Bob') # Hello Bob !

### Pluralization

Pluralization is based on Rail i18n module. By passing a `count` variable to your translation, it will be pluralized. The translation value should be a dictionnary with at least the keys `one` and `many`. You can add a `zero` key when needed, if it is not present `many` will be used instead. Here is a sample usage.

    i18n.add_translation('mail_number', {
        'zero': 'You do not have any mail.',
        'one': 'You have a new mail.',
        'many': 'You have %{count} new mails.'
    })
    i18n.t('mail_number', count=0) # You do not have any mail.
    i18n.t('mail_number', count=1) # You have a new mail.
    i18n.t('mail_number', count=5) # 'You have 5 new mails.
