# Insurance Core - Frontend Monorepo

This is the frontend workspace for the Insurance Core project, organized as a Yarn Workspaces monorepo with multiple Next.js applications.

## 📁 Structure

```
frontend/
├── apps/
│   ├── customer_portal/    # Customer-facing app (Port 3000)
│   └── sales_funnel/       # Sales & marketing app (Port 3001)
├── package.json            # Workspace configuration
├── tsconfig.base.json      # Shared TypeScript config
└── .env.example            # Example environment variables
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Yarn (will be installed if not present)

### Installation

```bash
# From the frontend directory
yarn install
```

### Development

```bash
# Start customer portal (http://localhost:3000)
yarn dev:customer

# Start sales funnel (http://localhost:3001)
yarn dev:sales

# Start both apps concurrently
yarn dev:all
```

### Building

```bash
# Build customer portal
yarn build:customer

# Build sales funnel
yarn build:sales

# Build all apps
yarn build:all
```

### Testing & Linting

```bash
# Run tests for all apps
yarn test

# Run linter for all apps
yarn lint
```

## 📦 Applications

### Customer Portal (`apps/customer_portal`)

**Purpose**: Customer-facing policy management application

**Port**: 3000

**Features**:
- View insurance policies
- Manage policy holders
- Track claims
- Update personal information

**Run individually**:
```bash
yarn workspace customer-portal dev
```

### Sales Funnel (`apps/sales_funnel`)

**Purpose**: Sales and quote generation application

**Port**: 3001

**Features**:
- Request insurance quotes
- Compare insurance plans
- Purchase policies
- Talk to an agent

**Run individually**:
```bash
yarn workspace sales-funnel dev
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env.local` in the frontend root:

```bash
cp .env.example .env.local
```

Edit `.env.local` to configure:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

Environment variables prefixed with `NEXT_PUBLIC_` are available in the browser.

### TypeScript

Each app extends the shared `tsconfig.base.json` configuration. App-specific TypeScript settings can be configured in each app's `tsconfig.json`.

## 🐳 Docker

### Run with Docker Compose

From the project root:

```bash
# Start customer portal only
docker-compose up customer_portal

# Start sales funnel only
docker-compose up sales_funnel

# Start both apps
docker-compose up customer_portal sales_funnel

# Or start all services (backend, database, both frontends)
docker-compose up
```

## 📝 Adding a New App

1. Create a new directory under `apps/`:
   ```bash
   mkdir -p apps/new_app/src/app apps/new_app/public
   ```

2. Add `package.json` with app-specific configuration

3. Add `tsconfig.json` extending `../../tsconfig.base.json`

4. Create Next.js app structure in `src/app/`

5. Update root `package.json` scripts to include the new app

6. Create a Dockerfile for the new app

7. Add the app to `docker-compose.yml`

## 🛠️ Workspace Commands

### Working with Specific Apps

```bash
# Run a command in a specific workspace
yarn workspace <workspace-name> <command>

# Examples:
yarn workspace customer-portal dev
yarn workspace sales-funnel build
yarn workspace customer-portal test
```

### List All Workspaces

```bash
yarn workspaces info
```

### Install Dependency to Specific App

```bash
# Add to customer-portal
yarn workspace customer-portal add <package-name>

# Add to sales-funnel
yarn workspace sales-funnel add <package-name>

# Add to root (dev dependencies shared across all apps)
yarn add -W <package-name>
```

## 🧹 Cleaning

```bash
# Remove all node_modules and build artifacts
yarn clean

# Then reinstall
yarn install
```

## 📚 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Package Manager**: Yarn Workspaces
- **Testing**: Vitest
- **Linting**: ESLint with next/core-web-vitals

## 🔗 Related Documentation

- [CLAUDE.md](/CLAUDE.md) - Full project documentation
- [Backend README](/backend/README.md) - Backend API documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [Yarn Workspaces](https://classic.yarnpkg.com/en/docs/workspaces/)

## 🤝 Contributing

When working with this monorepo:

1. Always run `yarn install` from the frontend root, not individual apps
2. Use workspace commands to work with specific apps
3. Follow the existing app structure when creating new apps
4. Keep shared configuration in the root when possible
5. App-specific configuration should stay in the app directory

## 📄 License

See project root for license information.
