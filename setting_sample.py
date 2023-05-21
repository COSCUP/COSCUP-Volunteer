import os
# ----- flask ----- #
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 6699

# ----- Admin ----- #
# The uids to creating project via API /project
API_DEFAULT_OWNERS = ['00000000', ]

# ----- Google OAuth Login ----- #
# create a project on Google console(GCP)
# completed 'API & Services' >  'OAuth consent screen'
# create an OAuth 2.0 Client ID at 'API & Services' > 'Credentials'
# download the credential as 'client_secret.json'
CLIENT_SECRET = './client_secret.json'

# For session/cookie encryption
# os.urandom or uuid or anything more than 64bits
SECRET_KEY = '{{SECRET_KEY}}'

# e.g. 'volunteer.coscup.org'
DOMAIN = '{{DOMAIN}}'

# memcached container
MC_SERVERS = ['memcached', ]


# ----- MongoDB ----- #
MONGO_HOST = 'mongo'
MONGO_PORT = '27017'
MONGO_DBNAME = '{{DB_NAME}}'
MONGO_MOCK = True

# ----- RabbitMQ ----- #
RABBITMQ = 'guest:guest@rabbitmq:5672'

# ----- AWS ----- #
# create api token from AWS IAM
AWS_ID = '{{AWS_ID}}'
AWS_KEY = '{{AWS_KEY}}'
AWS_SES_FROM = {'name': '{{SENDER_NAME}}', 'mail': '{{SENDER_MAIL}}'}
AWS_LIST_UNSUBSCRIBE = '<mailto:{{YOUR_MAIL}}>'

# for alert/error mail, send to admin
ADMIN_To = {'name': '{{YOUR_NAME}}', 'mail': '{{YOUR_MAIL}}'}

# ----- IPINFO ----- #
# ipinfo.io api token, for parse ip info
IPINFO_TOKEN = '{{IPINFO_TOKEN}}'

# ----- Google Workspace ----- #
# you need to create another project at Google console(GCP), because this is
# using Google Workspace Admin SDK for manager users into Groups.
# admin scope:
#  - https://www.googleapis.com/auth/admin.directory.user
#  - https://www.googleapis.com/auth/admin.directory.group
# more settings guides:
#  - https://developers.google.com/admin-sdk/groups-settings/get_started
#  - https://developers.google.com/admin-sdk/reports/v1/guides/delegation#delegate_domain-wide_authority_to_your_service_account
GSUITE_JSON = '{{GSUITE_CERTIFICATE_FILE}}'
GSUITE_ADMIN = '{{GSUITE_SUPERVISOR_MAIL}}'

# ----- Mattermost ----- #
MATTERMOST_SLASH_VOLUNTEER = '{{MATTERMOST_SLASH_TOKEN}}'
MATTERMOST_BOT_ID = '{{MATTERMOST_BOT_ID}}'
MATTERMOST_BOT_TOKEN = '{{MATTERMOST_BOT_TOKEN}}'
MATTERMOST_BASEURL = 'https://chat.coscup.org/api/v4'
MATTERMOST_TEAM_ID = '1wfr5adsc3yfmk717j4g4f5ayo'

# ----- Gitlab ----- #
GITLAB_TOKEN = '{{GITLAB_TOKEN}}'

# ----- Telegram ----- #
TELEGRAM_TOKEN = '{{TELEGRAM_TOKEN}}'
TELEGRAM_WEBHOOK = 'https://%s/{{WEBHOOK_PATH}}' % DOMAIN

# ----- OpenAI ----- #
OPENAI_ARGS = {
    'token': '',
    'organization': '',
}

# ----- Pretalx ----- #
PRETALX_API_KEY = ''
EXCLUDE_SUBMISSIONS = []

# ----- TDX (Transport Data eXchange) ----- #
# This is used when connecting API for rail info
# You need to apply for api keys on tdx.transportdata.tw
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
