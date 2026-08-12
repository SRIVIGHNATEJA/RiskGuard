# Selenium Failure Screenshots — Infrastructure Troubleshooting Evidence

## What these screenshots show

The four PNG files that were originally committed in `docs/screenshots/failures/` 
all showed the Chrome browser error:

> **ERR_EMPTY_RESPONSE**  
> "This page isn't working. 127.0.0.1 didn't send any data."

## What this means

These screenshots do NOT demonstrate a defect in the RiskGuard application.  
They demonstrate an **infrastructure/environment failure**: the frontend server  
(Python `http.server` on port 8080) was not running at the time the Selenium  
tests attempted to connect.

## Root cause

During Phase 5 (Selenium automation), the test runner was started before the  
servers were confirmed ready. The browser launched and immediately received an  
empty response because the frontend had not yet bound to port 8080.

## Correction

- These screenshots were removed from the committed evidence in the cleanup commit.  
- They are retained locally under `docs/screenshots/failures/` for reference.  
- They are not presented as application defect evidence anywhere in this project.

## What valid Selenium test evidence looks like

A valid failure screenshot would show:
- The RiskGuard application UI loaded in the browser
- A visible assertion mismatch (e.g., wrong text in the result box)

The `ERR_EMPTY_RESPONSE` screenshots provide no value for application testing.
