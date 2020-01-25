# plantuml trick
watchdog script to generate images from plantuml files
 
## Setup
```sh
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

## Example

Use with [watchdog](https://github.com/gorakhargosh/watchdog)

```yaml
tricks:
  - plantuml_trick.Plantuml:
      patterns: ['*.plantuml', '*.puml']
      destination_suffix: .puml.svg
      source_directory: .
      destination_directory: .
      opts:
        - [--config, ./config]

```

```bash
watchmedo tricks-from tricks.yaml
```
## Credits
This package was created with Cookiecutter and the [sourceryai/python-best-practices-cookiecutter](https://github.com/sourceryai/python-best-practices-cookiecutter) project template.

