# plantuml trick

Converts PlantUML to images;

![Order-UML](./Order.puml.svg "UML Example")

## Example

Use with [watchdog](https://github.com/gorakhargosh/watchdog)

```
pip install pipenv watchdog
```
## Basic

Simple configuration mostly relying on defaults:

```yaml
tricks:
  -
    plantuml_trick.plantuml.PlantumlTrick:
      postprocess:
        mixed_line_ending: # 'auto', 'no', 'cr', 'crlf', 'lf'
          - '--fix=lf'
```
## Configuration Options

Disabled by default, there is an option to invoke `svgo` on the generated SVG files so to prettify them.

Other options control the behaviour of the watcher itself, such as `conjunction_removal` or `insert_infix`.

See below for possible config tweaks:

```yaml
tricks:
  -
    plantuml_trick.plantuml.PlantumlTrick:
      # see https://plantuml.com/command-line
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
      # --- Customization examples ---
      postprocess:
        # see https://github.com/pre-commit/pre-commit-hooks/tree/v2.4.0
        mixed_line_ending: # 'auto', 'no', 'cr', 'crlf', 'lf'
          - '--fix=lf'
        svg:
          docker_image: thorisalaptop/svgo
          # options -- see https://github.com/svg/svgo
          compile_opts:
            - "--pretty"
            - "--indent=4"
            - |-
              --config='{"plugins":[{"removeComments":false}]}'
```

## Customizing the theme of generated images

Example `.plantuml.cfg`:

```ini
skinparam monochrome true
skinparam defaultFontName "Ubuntu Mono, Fira Mono, Sans-Serif"
skinparam defaultFontSize 14
skinparam entityBackgroundColor white
skinparam linetype ortho
```

## Invoke the compiler on file changes

```
pip install git+https://github.com/Bonusnorm/plantuml_trick.git@0.0.1a1.dev1
```

### Using watchdog

```
pipenv run watchmedo tricks-from tricks.yaml
```

### On-Demand

If you want to trigger the script on your own or let your IDE invoke it, use the following:

```
pipenv run makemedo_plantuml <filenames>
```

### As a pre-commit step



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
