# Scaffoldr

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Scaffoldr is a fast and simple CLI tool for instantly generating configuration files and boilerplates for your favorite DevOps and infrastructure tools.**

Stop searching for documentation and examples. With Scaffoldr, you can interactively generate validated and ready-to-use configuration files for tools like Borgmatic, Restic, and more, directly from your terminal.

## Why Scaffoldr?

In the world of DevOps and infrastructure management, setting up new tools often involves a repetitive cycle of finding documentation, copying boilerplate code, and tweaking it to fit your needs. This process is slow and error-prone.

Scaffoldr solves this problem by providing an interactive command-line interface that guides you through the process of creating configuration files. It uses pre-defined templates and prompts to ensure that you generate a complete and correct setup every time.

### Features

- **Interactive Generation**: Guides you through configuration with simple prompts.
- **Backup Configuration**: Generates configuration for backup tools like Borgmatic and Autorestic.
- **Validation**: Ensures required fields are present and correct.
- **Single Binary**: Distributed as a single, dependency-free executable.

## Getting Started

### Installation

Scaffoldr is distributed as a single binary, making installation quick and easy.

1.  Download the latest `scaffoldr` binary for your operating system from the [GitHub Releases](https://github.com/gowdhamp/scaffoldr/releases) page.
2.  Place the binary in a directory included in your system's `PATH` (e.g., `/usr/local/bin` on Linux/macOS).
3.  Make the binary executable:
    ```sh
    chmod +x /path/to/your/scaffoldr
    ```

## Usage

To use Scaffoldr, run the executable followed by the command for the tool you wish to configure.


```sh
scaffoldr -h
```

### Example: Create a Borgmatic Configuration

To generate a `borgmatic.yaml` file, run the `create-borgmatic` subcommand and follow the interactive prompts.

```sh
scaffoldr backup create-borgmatic
```

This will launch an interactive wizard that asks for repository paths, retention policies, and other necessary details, and then generates a complete `borgmatic.yaml` file for you.

### Example: Create an Autorestic Configuration

To generate an `autorestic.yaml` file, run the `create-autorestic` subcommand and follow the interactive prompts.

```sh
scaffoldr backup create-autorestic
```

This will launch an interactive wizard that asks for location, backend, and other necessary details, and then generates a complete `autorestic.yaml` file for you.

## License

Distributed under the MIT License. See `LICENSE` for more information.
