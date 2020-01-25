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
  - plantuml_trick.compiler.PlantumlTrick:
      src_dir: .
      patterns: ["*.puml","*.plantuml"]
      docker_image: miy4/plantuml
      compile_opts:
        - "-config .plantuml.cfg"
        - "-tsvg"
        - "-failfast2"
        - "-charset utf-8"

```

```bash
watchmedo tricks-from tricks.yaml
```
## Credits
This package was created with Cookiecutter and the [sourceryai/python-best-practices-cookiecutter](https://github.com/sourceryai/python-best-practices-cookiecutter) project template.

