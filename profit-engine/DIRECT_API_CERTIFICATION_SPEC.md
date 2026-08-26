# PROFIT ENGINE — YANDEX DIRECT API CERTIFICATION SPECIFICATION

Status: MINIMAL APPLICATION SPEC v0.2
Updated: 2026-08-26

## Purpose

Profit Engine is an internal application for the owner's own Yandex Direct advertising account(s). It automates collection of campaign data and statistics and is intended to support internal advertising analytics and routine campaign management.

## Direct API functions

Initial functions:

1. Read campaigns, ad groups, ads, statuses and campaign settings.
2. Obtain statistics and reports for impressions, clicks, spend and other supported advertising metrics.
3. Synchronize Direct data with the application's internal reporting database.

Planned management functions:

1. Update permitted campaign parameters.
2. Pause and resume campaigns.
3. Update campaign budgets and other supported settings according to internal operator rules.

## Technical implementation

- Language: Python 3.12.
- Protocol: HTTPS + JSON.
- API: Yandex Direct API v5.
- Authentication: OAuth 2.0 using the registered Yandex OAuth application `Profit Engine`.
- The application does not store or use interactive Yandex passwords.

## Interaction scheme

1. The application receives an OAuth token for an authorized Yandex Direct user.
2. It sends HTTPS/JSON requests to Yandex Direct API services.
3. Read responses are stored in the application's internal database for reporting and analysis.
4. When management functions are enabled, permitted changes are sent to Direct API after validation by the application's internal rules.
5. API errors are logged and retried only when appropriate.

## New capabilities

The application reduces manual work by automatically collecting Direct statistics and campaign settings into one internal reporting system and by enabling controlled execution of routine campaign-management operations through the Direct API.

## Development stage

The OAuth application is registered. The first implementation stage is read-only collection and reporting. Campaign-management functions will be enabled after internal testing.

## Credential handling

OAuth credentials and tokens are stored outside source code in secure secret storage. No passwords or OAuth secret values are included in application documentation.
