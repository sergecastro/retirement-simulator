# Family Forecast — Project Context

## What This Is
Retirement planning SaaS with three domains:
- familyforecast.ai (landing page)
- intake.familyforecast.ai / familyforecast.lovable.app (Lovable INTAKE)
- app.familyforecast.ai (Streamlit Analysis on Render)

## Architecture
- Streamlit Python app (~20 modules)
- External Supabase: ebhzvauommuhqlcswdil (pending_intake table)
- Lovable Cloud Supabase: wyjtrpapfrkohcttiznf (anonymous_vaults)
- AES-256-GCM encryption, anonymous vaults

## Key Files
- app.py: Main routing, URL params (session handler lines 357-399)
- utils/supabase_sync.py: transform_lovable_to_streamlit(), load_pending_intake()
- utils/password_crypto.py: Encryption

## Current Status (Feb 9, 2026)
- Frictionless flow: WORKING on familyforecast.lovable.app
- Custom domain intake.familyforecast.ai: BROKEN (serving old code)
- Quick Mode partner: BROKEN
- Full Mode: UNTESTED with new fixes

## Rules
- Max 500 lines per file
- Git commit before major changes
- "For Educational Purposes" disclaimer required
- Never suggest incognito/localStorage clearing for testing