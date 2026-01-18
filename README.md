## <https://alexsavio.github.io>

---

![Publish Github Pages](https://github.com/alexsavio/alexsavio.github.io/workflows/Publish%20Github%20Pages/badge.svg?branch=dev&event=page_build)

## Development

This blog is powered by [Pelican](https://getpelican.com/) and uses [uv](https://github.com/astral-sh/uv) for dependency management and [just](https://github.com/casey/just) for task automation.

### Quick Start

1. Install dependencies:

    ```bash
    just install
    ```

2. Build and serve the blog:

    ```bash
    just serve-dev
    ```

3. View available commands:

    ```bash
    just --list
    ```

See [MIGRATION.md](MIGRATION.md) for more details on the project setup.
