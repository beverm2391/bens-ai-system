# Project Structure

Root directory: `bens-ai-system/`
Electron app root: `portal/`

```
bens-ai-system/
├── portal/                 # Electron app root
│   ├── src/               # TypeScript source code
│   │   ├── main.ts        # Main process
│   │   └── preload.ts     # Preload script
│   ├── dist/              # Compiled JavaScript
│   ├── node_modules/      # Dependencies
│   ├── index.html         # Main window
│   ├── package.json       # Dependencies and scripts
│   └── tsconfig.json      # TypeScript config
└── ... other project files
```

# Technical Stack

- Electron application using TypeScript and ES6 modules
- TypeScript compiled to ES6 modules in dist/
- Module imports use `.js` extension for compiled files
- All JavaScript files use `type="module"` when imported in HTML
- Node integration is disabled for security
- IPC communication handled through preload scripts

# Module Import Examples

```ts
// TypeScript imports
import { app, BrowserWindow } from 'electron';
import { fileURLToPath } from 'url';
import path from 'path';

// TypeScript interfaces
interface WindowConfig {
  width: number;
  height: number;
}

// Named exports
export { someFunction };
export const config: WindowConfig = {
  width: 800,
  height: 600
};

// Default exports
export default class MyClass {
  private config: WindowConfig;
  // ...
}
```
