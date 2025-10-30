# E2E Tests

End-to-end tests for the IdP Notifications Foundry app using Playwright.

## Tests Included

- **Workflow Action Verification**: Verifies that the app's exposed actions are discoverable in Fusion SOAR workflow builder

## About This App

This app provides monitoring functions for IdP domain controllers and connectors. The functions are exposed as workflow actions via `workflow_integration` with `system_action: false` in the manifest. The E2E tests verify that both actions are properly discoverable in the Fusion SOAR workflow builder.

## Setup

```bash
npm ci
npx playwright install chromium
cp .env.sample .env
# Edit .env with your credentials
```

## Run Tests

```bash
npm test              # All tests
npm run test:debug    # Debug mode
npm run test:ui       # Interactive UI
```

## Environment Variables

```env
APP_NAME=foundry-sample-idp-notifications
FALCON_BASE_URL=https://falcon.us-2.crowdstrike.com
FALCON_USERNAME=your-username
FALCON_PASSWORD=your-password
FALCON_AUTH_SECRET=your-mfa-secret
```

**Important:** The `APP_NAME` must exactly match the app name as deployed in Falcon.

## Test Flow

1. **Setup**: Authenticates and installs the app
2. **Workflow Action Verification**:
   - Creates a new workflow with an on-demand trigger
   - Opens the action picker
   - Searches for both exposed actions
   - Verifies both actions are discoverable in the workflow builder
3. **Teardown**: Uninstalls the app

## CI/CD

Tests run automatically in GitHub Actions on push/PR to main. The workflow deploys the app, runs tests, and cleans up.
