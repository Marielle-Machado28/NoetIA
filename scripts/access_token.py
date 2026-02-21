from google_auth_oauthlib.flow import InstalledAppFlow
# Esto abre una ventana en tu navegador para que autorices a NoetIA
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/calendar'])
creds = flow.run_local_server(port=0)
print(f"Tu TOKEN: {creds.token}")
print(f"Tu REFRESH_TOKEN: {creds.refresh_token}")