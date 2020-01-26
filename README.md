# plantuml trick
watchdog script to generate images from plantuml files

## Example

Use with [watchdog](https://github.com/gorakhargosh/watchdog)

```yaml
tricks:
  - plantuml_trick.compiler.PlantumlTrick:
      compile_opts:
        # ------------------------------ Defaults: -----------------
        - "-tsvg"
        - "-failfast2"
        - "-charset utf-8"
        # --- Customization examples ---
        # - "-output diagrams"
        # - "-config .plantuml.cfg"
      # -------------------------------- Defaults: -----------------
      src_dir: .
      patterns: ["*.puml","*.plantuml"]
      docker_image: miy4/plantuml
      insert_infix: true
      conjunction_removal: true

```

Example `.plantuml.cfg`:

```ini
skinparam monochrome true
skinparam defaultFontName "Ubuntu Mono, Fira Mono, Sans-Serif"
skinparam defaultFontSize 14
skinparam entityBackgroundColor white
skinparam linetype ortho

```

```bash
watchmedo tricks-from tricks.yaml
```

## Dev Setup
```sh
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

## Credits
This package was created with Cookiecutter and the [sourceryai/python-best-practices-cookiecutter](https://github.com/sourceryai/python-best-practices-cookiecutter) project template.
In addition, I learned much from exploring [yejianye/watchdog_tricks](https://github.com/yejianye/watchdog-tricks/tree/master/watchdog_tricks).

