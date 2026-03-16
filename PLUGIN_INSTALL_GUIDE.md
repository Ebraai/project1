# Plugin Installation Guide

This guide explains how to install, manage, and remove plugins in the project.

## Prerequisites

Before installing any plugin, ensure you have the following:

- Node.js >= 16.x (for Node.js-based plugins)
- npm or yarn package manager
- Project dependencies installed (`npm install`)

---

## Installation Methods

### Method 1: Install via npm / yarn

Most plugins are distributed as npm packages. Use one of the following commands:

```bash
# Using npm
npm install <plugin-name>

# Using yarn
yarn add <plugin-name>
```

**Example:**

```bash
npm install my-awesome-plugin
```

---

### Method 2: Install via the Project CLI

If the project provides a CLI tool, you can install plugins directly:

```bash
# Install a plugin
npx project-cli plugin install <plugin-name>

# Install a specific version
npx project-cli plugin install <plugin-name>@<version>
```

---

### Method 3: Install from a Local Path

To install a plugin from a local directory (useful during development):

```bash
npm install /path/to/local/plugin
```

---

### Method 4: Install from a Git Repository

You can also install a plugin directly from a GitHub or GitLab repository:

```bash
npm install github:<username>/<repo>

# Example
npm install github:myorg/my-plugin
```

---

## Registering a Plugin

After installation, register the plugin in your project configuration file (e.g., `config.js`, `config.json`, or `.pluginrc`):

```js
// config.js
module.exports = {
  plugins: [
    require('my-awesome-plugin'),
    // Add more plugins here
  ],
};
```

Or, if your config uses JSON:

```json
{
  "plugins": [
    "my-awesome-plugin"
  ]
}
```

---

## Plugin Configuration

Some plugins accept options. Pass a configuration object when registering:

```js
// config.js
module.exports = {
  plugins: [
    [require('my-awesome-plugin'), { option1: true, option2: 'value' }],
  ],
};
```

---

## Listing Installed Plugins

To see all currently installed plugins:

```bash
npm list --depth=0
```

Or, if using the project CLI:

```bash
npx project-cli plugin list
```

---

## Updating a Plugin

```bash
# Update to the latest version
npm update <plugin-name>

# Update to a specific version
npm install <plugin-name>@<version>
```

---

## Removing a Plugin

```bash
# Using npm
npm uninstall <plugin-name>

# Using yarn
yarn remove <plugin-name>
```

Don't forget to also remove it from your configuration file after uninstalling.

---

## Troubleshooting

### Plugin not found

- Ensure the plugin is listed in your `package.json` under `dependencies` or `devDependencies`.
- Run `npm install` to make sure all dependencies are installed.

### Plugin fails to load

- Check the plugin version is compatible with the current project version.
- Review the plugin's documentation for any peer dependency requirements.
- Look for error messages in the console and check the plugin's issue tracker.

### Permission errors

- On Unix systems, you may need to prefix commands with `sudo`:
  ```bash
  sudo npm install -g <plugin-name>
  ```
- Alternatively, configure npm to use a different directory to avoid permission issues.

---

## Further Reading

- [npm documentation](https://docs.npmjs.com/)
- [yarn documentation](https://yarnpkg.com/getting-started)
- Project-specific plugin API docs (see `docs/` folder)
