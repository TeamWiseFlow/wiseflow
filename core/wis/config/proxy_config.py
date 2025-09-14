# for PLATFORMS, you can assign different proxy providers
# none\local\kdl_x options for now
# if you choose kuaidaili, you should config kdl_x dict first
# if you choose local, you should ensure put the right proxy file in {PROJECT_ROOT}/proxy_setting.json
# and the json file should be like this:
# [
#     {
#         "ip": "http://127.0.0.1",
#         "port": 8080,
#         "user": "user",
#         "password": "password",
#         "life_time": 17  # in minutes, 0 means never expire
#     }
# ]

# WEB_PROXY = 'local'
WEB_PROXY = 'none'
# WEB_PROXY = 'kdl_1'
# kdl_1 = {
#     "SECERT_ID": "ow7eguqh9wka9gaiep6h",
#     "SIGNATURE": "fv4tnox6mote3kumyl81dklp3sxv9nfk",
#     "USER_NAME": "d4742572977",
#     "USER_PWD": "qrkfs99v"
# }
