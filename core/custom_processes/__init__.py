from .crawler_configs import DEFAULT_CRAWLER_CONFIG, NEED_LOGIN_CRAWLER_CONFIG

# use a pure domain name to identify the crawler config
crawler_config_map = {'default': DEFAULT_CRAWLER_CONFIG, 
                      'wsj.com': NEED_LOGIN_CRAWLER_CONFIG}
