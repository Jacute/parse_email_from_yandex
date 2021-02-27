# https://github.com/2captcha/2captcha-python
from twocaptcha import TwoCaptcha
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

api_key = os.getenv('APIKEY_2CAPTCHA', '555335d2596c15fde65cfe3e74b61877')

solver = TwoCaptcha(api_key)

try:
    result = solver.normal('captchaimg.jpg')
    print(result)

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))