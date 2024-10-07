
// Problems
1. Received invalid response to GSSAPI negotiation: S
```bash
Add this line is `settings.py` inside DATABASES
        'OPTIONS': {
            'gssencmode': 'disable',  # Disable GSSAPI encryption
            'sslmode': 'require',  # SSL might be required by Supabase
        }
```

